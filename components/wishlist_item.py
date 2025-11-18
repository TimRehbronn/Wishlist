import streamlit as st

class WishlistItem:
    def __init__(self, gift_name, purchase_link, is_gifted=False):
        self.gift_name = gift_name
        self.purchase_link = purchase_link
        self.is_gifted = is_gifted

    def display(self, index):
        """Display wishlist item as a modern widget"""
        # Container mit ausgegrautem Hintergrund wenn bereits verschenkt
        if self.is_gifted:
            container = st.container()
            with container:
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f0f0f0;
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 10px;
                        opacity: 0.6;
                    ">
                        <h4 style="color: #666;">{self.gift_name}</h4>
                        <p style="color: #888;">🔗 <a href="{self.purchase_link}" target="_blank" style="color: #888;">{self.purchase_link}</a></p>
                        <p style="color: #4CAF50; font-weight: bold;">✅ Wird verschenkt</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            # Normales editierbares Widget
            with st.container():
                col1, col2, col3 = st.columns([3, 3, 1])
                
                with col1:
                    st.markdown(f"**🎁 {self.gift_name}**")
                
                with col2:
                    if self.purchase_link:
                        st.markdown(f"[🔗 Link zum Kaufen]({self.purchase_link})")
                
                with col3:
                    if st.button("🎅", key=f"gift_{index}", help="Ich möchte das schenken"):
                        return "toggle_gift"
                    
                # Delete button
                if st.button("🗑️", key=f"delete_{index}", help="Löschen"):
                    return "delete"
                
                st.divider()
        
        return None

    def to_dict(self):
        return {
            "gift_name": self.gift_name,
            "purchase_link": self.purchase_link,
            "is_gifted": self.is_gifted
        }