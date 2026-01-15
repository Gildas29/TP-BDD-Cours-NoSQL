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
    """Assure que ki / max_ki sont bien des float pour éviter l'erreur PyArrow."""
    for c in chars:
        for field in ("ki", "max_ki"):
            val = c.get(field, 0)
            try:
                c[field] = float(val) if val is not None else 0.0
            except (ValueError, TypeError):
                c[field] = 0.0
    return chars


def render_page():
    st.title("🟠 Interface Dragon Ball (MongoDB)")

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
            # Normaliser les champs numériques pour éviter ArrowTypeError. [web:160]
            chars = _normalize_numeric_fields(chars)

            # Vue tableau (toujours utile)
            df = pd.DataFrame(chars)
            st.dataframe(df, use_container_width=True)

            st.markdown("### Cartes des personnages")

            # Affichage en cartes graphiques
            cols = st.columns(3)
            for idx, c in enumerate(chars):
                col = cols[idx % 3]
                with col:
                    st.markdown(f"#### {c.get('name', 'Sans nom')}")
                    if c.get("image"):
                        st.image(c["image"], use_container_width=True)
                    st.write(f"**Affiliation / Race :** {c.get('race', 'N/A')}")
                    st.write(f"**Genre :** {c.get('gender', 'N/A')}")
                    st.write(
                        f"**Ki :** {c.get('ki', 'N/A')} / {c.get('max_ki', 'N/A')}"
                    )
                    desc = c.get("description", "")
                    if desc:
                        st.caption(desc[:180] + ("..." if len(desc) > 180 else ""))

    # --- Onglet 2 : Ajout ---
    with tab_add:
        st.subheader("Ajouter un nouveau personnage")

        name = st.text_input("Nom")
        race = st.text_input("Affiliation / Race")
        gender = st.selectbox("Genre", options=["", "Male", "Female", "Other"])
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
                    "gender": gender or None,
                    "ki": float(ki),
                    "max_ki": float(max_ki),
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
            chars = _normalize_numeric_fields(chars)
            ids = [c["_id"] + " - " + str(c.get("name", "")) for c in chars]
            selected = st.selectbox(
                "Choisis un personnage à modifier", options=[""] + ids
            )

            if selected:
                selected_id = selected.split(" - ")[0]
                doc = get_character_by_id(selected_id)

                if doc:
                    # Normaliser pour les champs numériques
                    doc = {
                        **doc,
                        "ki": float(doc.get("ki", 0) or 0),
                        "max_ki": float(doc.get("max_ki", 0) or 0),
                    }

                    name = st.text_input("Nom", value=doc.get("name", ""))
                    race = st.text_input(
                        "Affiliation / Race", value=doc.get("race", "")
                    )
                    gender = st.selectbox(
                        "Genre",
                        options=["", "Male", "Female", "Other"],
                        index=["", "Male", "Female", "Other"].index(
                            doc.get("gender", "") if doc.get("gender", "") in ["Male", "Female", "Other"] else ""
                        ),
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
                    image = st.text_input(
                        "URL de l'image",
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
                            "image": image,
                        }
                        update_character(selected_id, updates)
                        st.success(
                            "Personnage mis à jour. Rafraîchis la page pour voir les changements."
                        )