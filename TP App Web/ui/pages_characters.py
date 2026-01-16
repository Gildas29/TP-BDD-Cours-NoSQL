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


def _normalize_numeric_fields(chars):
    """Assure que ki / max_ki sont bien des float pour éviter les erreurs de conversion."""
    for c in chars:
        for field in ("ki", "max_ki"):
            val = c.get(field, 0)
            try:
                c[field] = float(val) if val is not None else 0.0
            except (ValueError, TypeError):
                c[field] = 0.0
    return chars


def render_page():
    st.title("🟠 Personnages Dragon Ball")

    tab_list, tab_add, tab_edit = st.tabs(
        ["📋 Liste / cartes", "➕ Ajouter", "✏️ Modifier"]
    )

    # --- Onglet 1 : Liste + cartes graphiques ---
    with tab_list:
        st.subheader("Liste des personnages")
        chars = get_all_characters()

        if not chars:
            st.info("Aucun personnage trouvé dans la collection.")
        else:
            # Normaliser les champs numériques.
            chars = _normalize_numeric_fields(chars)

            # ---- Tableau limité à name / description / gender / ki ----
            table_rows = []
            for c in chars:
                table_rows.append(
                    {
                        "name": c.get("name", ""),
                        "description": c.get("description", ""),
                        "gender": c.get("gender", ""),
                        "ki": c.get("ki", 0.0),
                    }
                )

            df = pd.DataFrame(table_rows)
            st.dataframe(df, use_container_width=True)

            # ---- Cartes graphiques avec bouton Supprimer ----
            st.markdown("### Cartes des personnages")

            cols = st.columns(3)
            for idx, c in enumerate(chars):
                col = cols[idx % 3]
                with col:
                    doc_id = c.get("_id")  # str (converti dans get_all_characters)

                    st.markdown(f"#### {c.get('name', 'Sans nom')}")
                    # Chemin local relatif (ex: images/goku.png) ou URL complète. [web:236]
                    if c.get("image"):
                        st.image(c["image"], use_container_width=True)
                    st.write(f"**Genre :** {c.get('gender', 'N/A')}")
                    st.write(f"**Ki :** {c.get('ki', 'N/A')}")
                    desc = c.get("description", "")
                    if desc:
                        st.caption(desc[:180] + ("..." if len(desc) > 180 else ""))

                    # Bouton supprimer spécifique à cette carte
                    if doc_id and st.button(
                        "🗑️ Supprimer", key=f"delete_card_{doc_id}"
                    ):
                        delete_character(doc_id)
                        st.success(f"Personnage supprimé : {c.get('name', '')}")
                        st.experimental_rerun()

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

    # --- Onglet 3 : Modification ---
    with tab_edit:
        st.subheader("Modifier un personnage existant")

        chars = get_all_characters()
        if not chars:
            st.info("Aucun personnage à modifier.")
        else:
            chars = _normalize_numeric_fields(chars)

            # On construit :
            # - display_names : ce que l'utilisateur voit (nom, éventuellement suffixe)
            # - id_by_label : mapping label -> _id
            display_names = []
            id_by_label = {}

            for c in chars:
                base_name = str(c.get("name", "Sans nom"))
                label = base_name

                # Si plusieurs persos ont le même nom, ajoute un suffixe avec un bout de l'id
                if base_name in id_by_label:
                    label = f"{base_name} ({c['_id'][:6]})"

                display_names.append(label)
                id_by_label[label] = c["_id"]

            selected_label = st.selectbox(
                "Choisis un personnage à modifier", options=[""] + display_names
            )

            if selected_label:
                selected_id = id_by_label[selected_label]
                doc = get_character_by_id(selected_id)

                if doc:
                    doc = {
                        **doc,
                        "ki": float(doc.get("ki", 0) or 0),
                        "max_ki": float(doc.get("max_ki", 0) or 0),
                    }

                    name = st.text_input("Nom", value=doc.get("name", ""))
                    race = st.text_input(
                        "Affiliation / Race", value=doc.get("race", "")
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
                    )
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

                    st.markdown(
                        "Chemin de l'image (exemple local : `images/goku.png`, "
                        "ou URL complète : `https://...`)"
                    )
                    image_path = st.text_input(
                        "Chemin / URL de l'image",
                        value=doc.get("image", ""),
                    )

                    if st.button("💾 Enregistrer les modifications"):
                        updates = {
                            "name": name,
                            "race": race,
                            "gender": gender or None,
                            "ki": float(ki),
                            "max_ki": float(max_ki),
                            "description": description,
                            "image": image_path,
                        }
                        update_character(selected_id, updates)
                        st.success(
                            "Personnage mis à jour. Rafraîchis la page pour voir les changements."
                        )
