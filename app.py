import streamlit as st
from utils.data_handler import (
    get_all_wishlists, 
    create_wishlist, 
    load_wishlist, 
    save_wishlist,
    verify_wishlist_password
)
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

# Application title
st.markdown('<h1 class="big-title">🎄 Weihnachts-Wunschliste 🎁</h1>', unsafe_allow_html=True)

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
    
    # Item input form
    st.subheader("➕ Neues Geschenk hinzufügen")
    with st.form(key='item_form', clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            gift_name = st.text_input("🎁 Geschenk Name", placeholder="z.B. Buch, Spielzeug, ...")
        
        with col2:
            purchase_link = st.text_input("🔗 Kauflink (optional)", placeholder="https://...")
        
        submit_button = st.form_submit_button("Hinzufügen", use_container_width=True)
        
        if submit_button and gift_name:
            item = {
                "gift_name": gift_name,
                "purchase_link": purchase_link,
                "is_gifted": False
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
        items_to_delete = []
        items_to_toggle = []
        
        for index, item in enumerate(wishlist_data['items']):
            item_display = WishlistItem(
                item['gift_name'],
                item['purchase_link'],
                item.get('is_gifted', False)
            )
            action = item_display.display(index)
            
            if action == "delete":
                items_to_delete.append(index)
            elif action == "toggle_gift":
                items_to_toggle.append(index)
        
        # Process deletions (in reverse order to maintain indices)
        for index in reversed(items_to_delete):
            wishlist_data['items'].pop(index)
            save_wishlist(st.session_state.current_wishlist_id, wishlist_data)
            st.rerun()
        
        # Process gift toggles
        for index in items_to_toggle:
            wishlist_data['items'][index]['is_gifted'] = True
            save_wishlist(st.session_state.current_wishlist_id, wishlist_data)
            st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>🎄 Frohe Weihnachten! 🎅</p>", unsafe_allow_html=True)