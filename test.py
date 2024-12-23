import streamlit as st

# value = st.number_input("Value")
# text = f""" 
# # <span style="font-size:24px;">Title</span>
# """


# # Initialize session state
# if "show_expander" not in st.session_state:
#     st.session_state.show_expander = False

# # Toggle expander visibility based on button click
# if st.button("Toggle Expander"):
#     st.session_state.show_expander = not st.session_state.show_expander

# # Show the content based on the state

# with st.expander(st.markdown(text, unsafe_allow_html=True), expanded=st.session_state.show_expander):
#     st.write("This expander is dynamically controlled by the button.")
#     st.text_input("Input something here")




# # Create an expander
# with st.expander(r"$\textsf{\Huge Pipeline Selection}$"):
#     st.markdown("This text is styled using injected CSS.")


# def change_label_style(label, font_size='12px', font_color='black', font_family='sans-serif'):
#     html = f"""
#     <script>
#         var elems = window.parent.document.querySelectorAll('p');
#         var elem = Array.from(elems).find(x => x.innerText == '{label}');
#         elem.style.fontSize = '{font_size}';
#         elem.style.color = '{font_color}';
#         elem.style.fontFamily = '{font_family}';
#     </script>
#     """
#     st.components.v1.html(html)

# label = "Pipeline Selection"
# with st.expander(label):
#     st.markdown("This text is styled using injected CSS.")
# change_label_style(label, '20px')


def change_label_style(label, font_size='12px', font_color='black', font_family='sans-serif', font_weight='normal'):
    html = f"""
    <script>
        var elems = window.parent.document.querySelectorAll('p');
        var elem = Array.from(elems).find(x => x.innerText == '{label}');
        elem.style.fontSize = '{font_size}';
        elem.style.color = '{font_color}';
        elem.style.fontFamily = '{font_family}';
        elem.style.fontWeight = '{font_weight}';
    </script>
    """
    st.components.v1.html(html)

