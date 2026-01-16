# ui/pages_characters.py
import streamlit as st
from db.mongo import (
    get_all_characters,
    get_character_by_id,
    insert_character,
    update_character,
    delete_character,
)


def _normalize_numeric_fields(chars):
    for c in chars:
        for field in ("ki", "max_ki"):
            val = c.get(field, 0)
            try:
                c[field] = float(val) if val is not None else 0.0
            except (ValueError, TypeError):
                c[field] = 0.0
    return chars


def render_page():
    # ---- Fond type Dragon Ball + texte sombre ----
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top, #ffe082 0%, #ffb300 35%, #f57c00 70%, #e65100 100%);
            color: #111111;  /* texte global plus sombre */
        }
        /* Titre, sous-titres, labels : texte foncé pour la lisibilité */
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp label, .stApp .stMarkdown, .stApp .stText, .stApp .stCaption {
            color: #111111 !important;
        }
        /* Cartes (colonnes) légèrement translucides pour faire ressortir le texte */
        .stApp .stColumn > div {
            padding: 0.5rem;
            background-color: rgba(255, 255, 255, 0.75);
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🟠 Personnages Dragon Ball")

    tab_list, tab_add = st.tabs(
        ["🃏 Cartes des personnages", "➕ Ajouter un personnage"]
    )

    # --- Onglet 1 : seulement les cartes (modifier + supprimer) ---
    with tab_list:
        st.subheader("Cartes des personnages")
        chars = get_all_characters()

        if not chars:
            st.info("Aucun personnage trouvé dans la collection.")
        else:
            chars = _normalize_numeric_fields(chars)

            cols = st.columns(3)
            for idx, c in enumerate(chars):
                col = cols[idx % 3]
                with col:
                    doc_id = c.get("_id")

                    st.markdown(f"### {c.get('name', 'Sans nom')}")
                    if c.get("image"):
                        st.image(c["image"], width=200)
                    st.write(f"**Genre :** {c.get('gender', 'N/A')}")
                    st.write(f"**Ki :** {c.get('ki', 'N/A')}")
                    desc = c.get("description", "")
                    if desc:
                        st.caption(desc[:180] + ("..." if len(desc) > 180 else ""))

                    col_mod, col_del = st.columns(2)

                    with col_mod:
                        if doc_id and st.button(
                            "✏️ Modifier", key=f"edit_card_{doc_id}"
                        ):
                            st.session_state["edit_id"] = doc_id

                    with col_del:
                        if doc_id and st.button(
                            "🗑️ Supprimer", key=f"delete_card_{doc_id}"
                        ):
                            delete_character(doc_id)
                            st.success(f"Personnage supprimé : {c.get('name', '')}")
                            st.rerun()

                    if (
                        doc_id
                        and st.session_state.get("edit_id", None) == doc_id
                    ):
                        st.markdown("#### Modifier ce personnage")
                        doc = get_character_by_id(doc_id)
                        if doc:
                            doc = {
                                **doc,
                                "ki": float(doc.get("ki", 0) or 0),
                                "max_ki": float(doc.get("max_ki", 0) or 0),
                            }

                            name = st.text_input(
                                "Nom", value=doc.get("name", ""), key=f"name_{doc_id}"
                            )
                            race = st.text_input(
                                "Affiliation / Race",
                                value=doc.get("race", ""),
                                key=f"race_{doc_id}",
                            )
                            gender_options = ["", "Male", "Female", "Other"]
                            current_gender = (
                                doc.get("gender", "")
                                if doc.get("gender", "") in gender_options
                                else ""
                            )
                            gender_index = gender_options.index(current_gender)

                            gender = st.selectbox(
                                "Genre",
                                options=gender_options,
                                index=gender_index,
                                key=f"gender_{doc_id}",
                            )
                            ki = st.number_input(
                                "Ki",
                                min_value=0.0,
                                step=1.0,
                                value=float(doc.get("ki", 0)),
                                key=f"ki_{doc_id}",
                            )
                            max_ki = st.number_input(
                                "Ki maximum",
                                min_value=0.0,
                                step=1.0,
                                value=float(doc.get("max_ki", 0)),
                                key=f"maxki_{doc_id}",
                            )
                            description = st.text_area(
                                "Description",
                                value=doc.get("description", ""),
                                height=100,
                                key=f"desc_{doc_id}",
                            )

                            st.markdown(
                                "Chemin de l'image (exemple local : `images/goku.png`, "
                                "ou URL complète : `https://...`)"
                            )
                            image_path = st.text_input(
                                "Chemin / URL de l'image",
                                value=doc.get("image", ""),
                                key=f"img_{doc_id}",
                            )

                            if st.button(
                                "💾 Enregistrer",
                                key=f"save_{doc_id}",
                            ):
                                updates = {
                                    "name": name,
                                    "race": race,
                                    "gender": gender or None,
                                    "ki": float(ki),
                                    "max_ki": float(max_ki),
                                    "description": description,
                                    "image": image_path,
                                }
                                update_character(doc_id, updates)
                                st.success("Personnage mis à jour.")
                                st.session_state["edit_id"] = None
                                st.rerun()

    # --- Onglet 2 : Ajout ---
    with tab_add:
        st.subheader("Ajouter un nouveau personnage")

        name = st.text_input("Nom")
        race = st.text_input("Affiliation / Race")
        gender = st.selectbox("Genre", options=["", "Male", "Female", "Other"])
        ki = st.number_input("Ki", min_value=0.0, step=1.0)
        max_ki = st.number_input("Ki maximum", min_value=0.0, step=1.0)
        description = st.text_area("Description", height=100)

        st.markdown(
            "Chemin de l'image (exemple local : `images/goku.png`, "
            "ou URL complète : `https://...`)"
        )
        image_path = st.text_input("Chemin / URL de l'image")

        if st.button("✅ Créer le personnage"):
            if not name:
                st.error("Le nom est obligatoire.")
            else:
                data = {
                    "name": name,
                    "race": race,
                    "gender": gender or None,
                    "ki": float(ki),
                    "max_ki": float(max_ki),
                    "description": description,
                    "image": image_path,
                }
                new_id = insert_character(data)
                st.success(f"Personnage créé avec l'id : {new_id}")
