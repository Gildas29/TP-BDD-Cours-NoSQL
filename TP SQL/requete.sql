-- Table des utilisateurs
CREATE TABLE utilisateurs (
  id            SERIAL        PRIMARY KEY,
  nom           VARCHAR(100)  NOT NULL,
  email         VARCHAR(255)  NOT NULL UNIQUE,
  mot_de_passe  VARCHAR(255)  NOT NULL,
  date_creation TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table des produits
CREATE TABLE produits (
  id          SERIAL         PRIMARY KEY,
  nom         VARCHAR(150)   NOT NULL,
  prix        DECIMAL(10,2)  NOT NULL,
  stock       INT            NOT NULL,
  description TEXT
);

-- Table des commandes
CREATE TABLE commandes (
  id             SERIAL        PRIMARY KEY,
  utilisateur_id INT           NOT NULL,
  date           TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  statut         VARCHAR(50)   NOT NULL,
  CONSTRAINT fk_commandes_utilisateur
    FOREIGN KEY (utilisateur_id)
    REFERENCES utilisateurs(id)
    ON DELETE CASCADE
);

-- Table des lignes de commande
CREATE TABLE lignes_commandes (
  id            SERIAL         PRIMARY KEY,
  commande_id   INT            NOT NULL,
  produit_id    INT            NOT NULL,
  quantite      INT            NOT NULL CHECK (quantite > 0),
  prix_unitaire DECIMAL(10,2)  NOT NULL,
  CONSTRAINT fk_lignes_commandes_commande
    FOREIGN KEY (commande_id)
    REFERENCES commandes(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_lignes_commandes_produit
    FOREIGN KEY (produit_id)
    REFERENCES produits(id)
    ON DELETE RESTRICT
);

-- Table des avis produits
CREATE TABLE avis (
  id             SERIAL       PRIMARY KEY,
  utilisateur_id INT          NOT NULL,
  produit_id     INT          NOT NULL,
  note           SMALLINT     NOT NULL CHECK (note BETWEEN 1 AND 5),
  commentaire    TEXT,
  CONSTRAINT fk_avis_utilisateur
    FOREIGN KEY (utilisateur_id)
    REFERENCES utilisateurs(id)
    ON DELETE CASCADE,
  CONSTRAINT fk_avis_produit
    FOREIGN KEY (produit_id)
    REFERENCES produits(id)
    ON DELETE CASCADE
);

-- Table des journaux d'activité (logs)
CREATE TABLE journaux_activite (
  id             SERIAL        PRIMARY KEY,
  utilisateur_id INT,
  action         VARCHAR(255)  NOT NULL,
  horodatage     TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_logs_utilisateur
    FOREIGN KEY (utilisateur_id)
    REFERENCES utilisateurs(id)
    ON DELETE SET NULL
);

-- Création d'utilisateurs
INSERT INTO utilisateurs (nom, email, mot_de_passe)
VALUES
  ('Alice',  'alice@example.com',  'motdepasse'),
  ('Bob',    'bob@example.com',    'motdepasse'),
  ('Charlie','charlie@example.com','motdepasse');

-- Création de produits
INSERT INTO produits (nom, prix, stock, description)
VALUES
  ('Clavier mécanique', 89.90, 10, 'Clavier mécanique RGB'),
  ('Souris sans fil',   29.99, 25, 'Souris ergonomique'),
  ('Écran 24 pouces',  159.00, 5,  'Écran Full HD 24"');