import streamlit as st
import html

class WishlistItem:
    def __init__(self, gift_name, purchase_link, is_gifted=False, price="", amazon_link="", is_highlight=False):
        self.gift_name = gift_name
        self.purchase_link = purchase_link
        self.is_gifted = is_gifted
        self.price = price
        self.amazon_link = amazon_link
        self.is_highlight = is_highlight

    def display(self, index, total_items):
        """Display wishlist item as a modern widget"""
        # Hintergrundfarbe: gelb für Highlights, grau für verschenkt, weiß sonst
        if self.is_gifted:
            bg_color = "#f0f0f0"
            border_color = "#e0e0e0"
            shadow = "0 1px 3px rgba(0,0,0,0.1)"
        elif self.is_highlight:
            bg_color = "#fffbea"
            border_color = "#ffc107"
            shadow = "0 2px 8px rgba(255, 193, 7, 0.3)"
        else:
            bg_color = "#ffffff"
            border_color = "#e0e0e0"
            shadow = "0 1px 3px rgba(0,0,0,0.1)"
        
        # Escape nur Text, nicht URLs
        safe_gift_name = html.escape(self.gift_name)
        safe_price = html.escape(self.price) if self.price else ""
        
        # Preis HTML
        price_html = f'<p style="color: #666; font-size: 0.9em; margin: 5px 0;">💰 {safe_price}</p>' if safe_price else ''
        
        # Links HTML - URLs NICHT escapen
        links_html = ""
        if self.purchase_link or self.amazon_link:
            link_parts = []
            if self.purchase_link:
                link_parts.append(f'<a href="{self.purchase_link}" target="_blank" style="color: #1976d2; text-decoration: none;">🔗 Kauflink</a>')
            if self.amazon_link:
                link_parts.append(f'<a href="{self.amazon_link}" target="_blank" style="color: #1976d2; text-decoration: none;">📦 Amazon</a>')
            links_html = f'<p style="margin: 5px 0;">{" • ".join(link_parts)}</p>'
        
        # Gesamter Container als HTML
        html_content = f"""
<div style="
    background-color: {bg_color};
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 15px;
    border: 2px solid {border_color};
    box-shadow: {shadow};
">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <h4 style="margin: 0; color: #333;">🎁 {safe_gift_name} {'✅' if self.is_gifted else ''}</h4>
    </div>
    {price_html}
    {links_html}
</div>
"""
        
        st.markdown(html_content, unsafe_allow_html=True)
        
        # Buttons außerhalb des HTML-Containers
        if not self.is_gifted:
            col_gift, col_up, col_down, col_delete, col_edit = st.columns([5, 1, 1, 1, 1])
            
            with col_gift:
                if st.button("🎅 Ich möchte das schenken", key=f"gift_{index}", use_container_width=True):
                    return {"action": "toggle_gift", "index": index}
            
            with col_up:
                if index > 0:
                    if st.button("⬆️", key=f"up_{index}", help="Nach oben"):
                        return {"action": "move_up", "index": index}
            
            with col_down:
                if index < total_items - 1:
                    if st.button("⬇️", key=f"down_{index}", help="Nach unten"):
                        return {"action": "move_down", "index": index}
            
            with col_delete:
                if st.button("🗑️", key=f"delete_{index}", help="Löschen"):
                    return {"action": "delete", "index": index}
            
            with col_edit:
                if st.button("✏️", key=f"edit_{index}", help="Bearbeiten"):
                    return {"action": "edit", "index": index}
        
        return None

    def to_dict(self):
        return {
            "gift_name": self.gift_name,
            "purchase_link": self.purchase_link,
            "is_gifted": self.is_gifted,
            "price": self.price,
            "amazon_link": self.amazon_link,
            "is_highlight": self.is_highlight
        }