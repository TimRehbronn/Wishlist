import streamlit as st
from utils.data_handler import (
    get_all_wishlists, 
    create_wishlist, 
    load_wishlist, 
    save_wishlist,
    verify_wishlist_password
)
from utils.remote_storage import remote_available
from components.wishlist_item import WishlistItem

# Page configuration
st.set_page_config(
    page_title="🎄 Weihnachts-Wunschliste",
    page_icon="🎁",
    layout="centered"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .big-title {
        text-align: center;
        color: #d32f2f;
        font-size: 3em;
        margin-bottom: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

# Application title + storage badge
st.markdown('<h1 class="big-title">🎄 Weihnachts-Wunschliste 🎁</h1>', unsafe_allow_html=True)

# Storage status badge
storage_label = "GitHub" if remote_available() else "Local"
badge_color = "#1976d2" if storage_label == "GitHub" else "#888"
st.markdown(
        f"""
        <div style="text-align:center; margin-top:-10px;">
            <span style="
                display:inline-block;
                padding:6px 10px;
                border-radius:12px;
                background:{badge_color};
                color:white;
                font-size:12px;
                letter-spacing:0.3px;
            ">Storage: {storage_label}</span>
        </div>
        """,
        unsafe_allow_html=True
)

# Optional diagnostics to help configure remote storage
with st.expander("🔧 Storage diagnostics", expanded=False):
    try:
        import os
        from utils.remote_storage import _get_secrets
        token, repo, prefix = _get_secrets()
        # Compute whether a token exists in secrets (top-level or [general])
        secrets_has_token = False
        try:
            if hasattr(st, "secrets"):
                if st.secrets.get("GH_TOKEN"):
                    secrets_has_token = True
                else:
                    gen = st.secrets.get("general")
                    if gen is not None and hasattr(gen, "get") and gen.get("GH_TOKEN"):
                        secrets_has_token = True
        except Exception:
            pass

        st.write({
            "remote_available": remote_available(),
            "GH_REPO": repo or "(missing)",
            "GH_PATH": prefix or "(missing)",
            "GH_TOKEN_present": bool(token),
            "ENV_has_token": bool(os.environ.get("GH_TOKEN")),
            "SECRETS_has_token": secrets_has_token,
        })
        if not remote_available():
            st.info("Add secrets in Streamlit Cloud: GH_TOKEN, GH_REPO, GH_PATH. After saving, wait ~1 minute and reload.")
        else:
            # Optional self-test to verify GitHub write access
            if st.button("Run remote self-test"):
                try:
                    from utils.remote_storage import _put_file, _get_file
                    import datetime
                    now = datetime.datetime.utcnow().isoformat() + "Z"
                    test_path = f"{prefix}/healthcheck.txt"
                    _put_file(token, repo, test_path, f"ok {now}".encode("utf-8"), "chore: remote storage healthcheck")
                    echoed = _get_file(token, repo, test_path)
                    if echoed and echoed.startswith("ok "):
                        st.success("Remote self-test passed: wrote and read healthcheck.txt")
                    else:
                        st.warning("Remote self-test wrote file but read-back content was unexpected.")
                except Exception as e:
                    st.error(f"Remote self-test failed: {e}")
    except Exception as e:
        st.warning(f"Diagnostics unavailable: {e}")

# Initialize session state
if 'current_wishlist_id' not in st.session_state:
    st.session_state.current_wishlist_id = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Main navigation
if st.session_state.current_wishlist_id is None:
    # Show list selection / creation screen
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📋 Bestehende Liste öffnen", "➕ Neue Liste erstellen"])
    
    with tab1:
        st.subheader("Wähle eine Wunschliste")
        wishlists = get_all_wishlists()
        
        if not wishlists:
            st.info("📭 Noch keine Wunschlisten vorhanden. Erstelle eine neue Liste!")
        else:
            # Display available wishlists
            for wishlist in wishlists:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### 🎅 {wishlist['name']}")
                with col2:
                    if st.button("Öffnen", key=f"open_{wishlist['id']}"):
                        st.session_state.current_wishlist_id = wishlist['id']
                        st.session_state.authenticated = False
                        st.rerun()
                st.markdown("---")
    
    with tab2:
        st.subheader("Neue Wunschliste erstellen")
        
        with st.form(key='create_wishlist_form'):
            new_list_name = st.text_input(
                "📝 Name der Wunschliste",
                placeholder="z.B. Tims Weihnachtswunschliste 2025"
            )
            new_list_password = st.text_input(
                "🔒 Passwort für diese Liste",
                type="password",
                placeholder="Wähle ein sicheres Passwort"
            )
            new_list_password_confirm = st.text_input(
                "🔒 Passwort bestätigen",
                type="password",
                placeholder="Passwort wiederholen"
            )
            
            create_button = st.form_submit_button("Liste erstellen", use_container_width=True)
            
            if create_button:
                if not new_list_name:
                    st.error("❌ Bitte gib einen Namen für die Liste ein!")
                elif not new_list_password:
                    st.error("❌ Bitte gib ein Passwort ein!")
                elif new_list_password != new_list_password_confirm:
                    st.error("❌ Die Passwörter stimmen nicht überein!")
                else:
                    wishlist_id = create_wishlist(new_list_name, new_list_password)
                    st.success(f"✅ Wunschliste '{new_list_name}' wurde erstellt!")
                    st.session_state.current_wishlist_id = wishlist_id
                    st.session_state.authenticated = True
                    st.rerun()

else:
    # Load current wishlist
    wishlist_data = load_wishlist(st.session_state.current_wishlist_id)
    
    if not wishlist_data:
        st.error("❌ Wunschliste nicht gefunden!")
        if st.button("Zurück zur Übersicht"):
            st.session_state.current_wishlist_id = None
            st.session_state.authenticated = False
            st.rerun()
        st.stop()
    
    # Password protection for the wishlist
    if not st.session_state.authenticated:
        st.markdown(f"### 🎅 {wishlist_data['name']}")
        st.markdown("---")
        
        password = st.text_input("🔒 Passwort eingeben", type="password", key="wishlist_password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Anmelden", use_container_width=True):
                if verify_wishlist_password(st.session_state.current_wishlist_id, password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Falsches Passwort!")
        
        with col2:
            if st.button("Zurück", use_container_width=True):
                st.session_state.current_wishlist_id = None
                st.session_state.authenticated = False
                st.rerun()
        
        st.stop()
    
    # Display wishlist (authenticated)
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"### 🎅 {wishlist_data['name']}")
    with col2:
        if st.button("🚪 Abmelden"):
            st.session_state.current_wishlist_id = None
            st.session_state.authenticated = False
            st.rerun()
    
    st.markdown("---")
    
    # Edit Dialog (if editing)
    if 'editing_item_index' in st.session_state and st.session_state.editing_item_index is not None:
        edit_index = st.session_state.editing_item_index
        item_to_edit = wishlist_data['items'][edit_index]
        
        st.subheader(f"✏️ Bearbeite: {item_to_edit['gift_name']}")
        
        with st.form(key='edit_form'):
            col1, col2 = st.columns(2)
            
            with col1:
                edit_gift_name = st.text_input("🎁 Geschenk Name", value=item_to_edit['gift_name'])
                edit_purchase_link = st.text_input("🔗 Kauflink", value=item_to_edit.get('purchase_link', ''))
                edit_price = st.text_input("💰 Preis", value=item_to_edit.get('price', ''))
            
            with col2:
                edit_amazon_link = st.text_input("📦 Amazon Link", value=item_to_edit.get('amazon_link', ''))
                edit_is_highlight = st.checkbox("⭐ Als Highlight markieren", value=item_to_edit.get('is_highlight', False))
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                save_button = st.form_submit_button("💾 Speichern", use_container_width=True)
            with col_cancel:
                cancel_button = st.form_submit_button("❌ Abbrechen", use_container_width=True)
            
            if save_button:
                wishlist_data['items'][edit_index] = {
                    "gift_name": edit_gift_name,
                    "purchase_link": edit_purchase_link,
                    "is_gifted": item_to_edit.get('is_gifted', False),
                    "price": edit_price,
                    "amazon_link": edit_amazon_link,
                    "is_highlight": edit_is_highlight
                }
                save_wishlist(st.session_state.current_wishlist_id, wishlist_data)
                st.session_state.editing_item_index = None
                st.success("✅ Änderungen gespeichert!")
                st.rerun()
            
            if cancel_button:
                st.session_state.editing_item_index = None
                st.rerun()
        
        st.markdown("---")
    
    # Item input form
    st.subheader("➕ Neues Geschenk hinzufügen")
    with st.form(key='item_form', clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            gift_name = st.text_input("🎁 Geschenk Name", placeholder="z.B. Buch, Spielzeug, ...")
            purchase_link = st.text_input("🔗 Kauflink (optional)", placeholder="https://...")
            price = st.text_input("💰 Preis (optional)", placeholder="z.B. 29,99€")
        
        with col2:
            amazon_link = st.text_input("📦 Amazon Link (optional)", placeholder="https://amazon.de/...")
            is_highlight = st.checkbox("⭐ Als Highlight markieren", help="Item wird gelb hervorgehoben")
        
        submit_button = st.form_submit_button("➕ Hinzufügen", use_container_width=True)
        
        if submit_button and gift_name:
            item = {
                "gift_name": gift_name,
                "purchase_link": purchase_link,
                "is_gifted": False,
                "price": price,
                "amazon_link": amazon_link,
                "is_highlight": is_highlight
            }
            wishlist_data['items'].append(item)
            save_wishlist(st.session_state.current_wishlist_id, wishlist_data)
            st.success(f"✅ '{gift_name}' wurde hinzugefügt!")
            st.rerun()
        elif submit_button:
            st.warning("⚠️ Bitte gib einen Geschenk-Namen ein!")
    
    st.markdown("---")
    
    # Display the wish list items
    st.subheader("🎁 Deine Wunschliste")
    
    if not wishlist_data.get('items') or len(wishlist_data.get('items', [])) == 0:
        st.info("📋 Deine Wunschliste ist noch leer. Füge oben ein Geschenk hinzu!")
    else:
        # Show statistics
        total_items = len(wishlist_data.get('items', []))
        gifted_items = sum(1 for item in wishlist_data.get('items', []) if item.get('is_gifted', False))
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Gesamt", total_items)
        col2.metric("Wird verschenkt", gifted_items)
        col3.metric("Noch offen", total_items - gifted_items)
        
        st.markdown("---")
        
        # Display items
        actions_to_process = []
        
        for index, item in enumerate(wishlist_data['items']):
            item_display = WishlistItem(
                item['gift_name'],
                item['purchase_link'],
                item.get('is_gifted', False),
                item.get('price', ''),
                item.get('amazon_link', ''),
                item.get('is_highlight', False)
            )
            action = item_display.display(index, len(wishlist_data['items']))
            
            if action:
                actions_to_process.append(action)
        
        # Process actions
        for action in actions_to_process:
            action_type = action.get('action')
            action_index = action.get('index')
            
            if action_type == "delete":
                wishlist_data['items'].pop(action_index)
                save_wishlist(st.session_state.current_wishlist_id, wishlist_data)
                st.rerun()
            
            elif action_type == "toggle_gift":
                wishlist_data['items'][action_index]['is_gifted'] = True
                save_wishlist(st.session_state.current_wishlist_id, wishlist_data)
                st.rerun()
            
            elif action_type == "move_up" and action_index > 0:
                # Tausche mit Item davor
                wishlist_data['items'][action_index], wishlist_data['items'][action_index - 1] = \
                    wishlist_data['items'][action_index - 1], wishlist_data['items'][action_index]
                save_wishlist(st.session_state.current_wishlist_id, wishlist_data)
                st.rerun()
            
            elif action_type == "move_down" and action_index < len(wishlist_data['items']) - 1:
                # Tausche mit Item danach
                wishlist_data['items'][action_index], wishlist_data['items'][action_index + 1] = \
                    wishlist_data['items'][action_index + 1], wishlist_data['items'][action_index]
                save_wishlist(st.session_state.current_wishlist_id, wishlist_data)
                st.rerun()
            
            elif action_type == "edit":
                # Setze edit mode in session state
                st.session_state.editing_item_index = action_index
                st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>🎄 Frohe Weihnachten! 🎅</p>", unsafe_allow_html=True)