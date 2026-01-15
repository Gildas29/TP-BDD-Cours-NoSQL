# ui/pages_characters.py
import streamlit as st
import pandas as pd
from db.mongo import (
    get_all_characters,
    get_character_by_id,
    insert_character,
    update_character,
    delete_character,
)


def render_page():
    st.title("🟠 Interface Dragon Ball (MongoDB)")

    tab_list, tab_add, tab_edit = st.tabs(
        ["📋 Liste / suppression", "➕ Ajouter", "✏️ Modifier"]
    )

    # --- Onglet 1 : Liste + suppression ---
    with tab_list:
        st.subheader("Liste des personnages")
        chars = get_all_characters()

        if not chars:
            st.info("Aucun personnage trouvé dans la collection.")
        else:
            df = pd.DataFrame(chars)
            st.dataframe(df, use_container_width=True)

            st.markdown("### Supprimer un personnage")
            ids = [c["_id"] + " - " + str(c.get("name", "")) for c in chars]
            selected = st.selectbox(
                "Choisis un personnage à supprimer", options=[""] + ids
            )

            if selected:
                selected_id = selected.split(" - ")[0]
                if st.button("🗑️ Supprimer ce personnage"):
                    delete_character(selected_id)
                    st.success(
                        "Personnage supprimé. Rafraîchis la page (Ctrl+R) pour mettre à jour la liste."
                    )

    # --- Onglet 2 : Ajout ---
    with tab_add:
        st.subheader("Ajouter un nouveau personnage")

        name = st.text_input("Nom")
        race = st.text_input("Race")
        ki = st.number_input("Ki", min_value=0.0, step=1.0)
        max_ki = st.number_input("Ki maximum", min_value=0.0, step=1.0)
        description = st.text_area("Description", height=100)
        image = st.text_input("URL de l'image")

        if st.button("✅ Créer le personnage"):
            if not name:
                st.error("Le nom est obligatoire.")
            else:
                data = {
                    "name": name,
                    "race": race,
                    "ki": ki,
                    "max_ki": max_ki,
                    "description": description,
                    "image": image,
                }
                new_id = insert_character(data)
                st.success(f"Personnage créé avec l'id : {new_id}")

    # --- Onglet 3 : Modification ---
    with tab_edit:
        st.subheader("Modifier un personnage existant")

        chars = get_all_characters()
        if not chars:
            st.info("Aucun personnage à modifier.")
        else:
            ids = [c["_id"] + " - " + str(c.get("name", "")) for c in chars]
            selected = st.selectbox(
                "Choisis un personnage à modifier", options=[""] + ids
            )

            if selected:
                selected_id = selected.split(" - ")[0]
                doc = get_character_by_id(selected_id)

                if doc:
                    name = st.text_input("Nom", value=doc.get("name", ""))
                    race = st.text_input("Race", value=doc.get("race", ""))
                    ki = st.number_input(
                        "Ki",
                        min_value=0.0,
                        step=1.0,
                        value=float(doc.get("ki", 0)),
                    )
                    max_ki = st.number_input(
                        "Ki maximum",
                        min_value=0.0,
                        step=1.0,
                        value=float(doc.get("max_ki", 0)),
                    )
                    description = st.text_area(
                        "Description",
                        value=doc.get("description", ""),
                        height=100,
                    )
                    image = st.text_input(
                        "URL de l'image",
                        value=doc.get("image", ""),
                    )

                    if st.button("💾 Enregistrer les modifications"):
                        updates = {
                            "name": name,
                            "race": race,
                            "ki": ki,
                            "max_ki": max_ki,
                            "description": description,
                            "image": image,
                        }
                        update_character(selected_id, updates)
                        st.success(
                            "Personnage mis à jour. Rafraîchis la page pour voir les changements."
                        )
