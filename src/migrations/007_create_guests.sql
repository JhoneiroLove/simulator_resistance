PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- Crear la tabla guests
CREATE TABLE IF NOT EXISTS guests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    age INTEGER NOT NULL,
    weight REAL NOT NULL,
    sex TEXT NOT NULL CHECK (sex IN ('M', 'F', 'Male','Femenine')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Actualizar la versión de la base de datos
UPDATE db_version SET version_num = 7 WHERE id = 1;

COMMIT;
PRAGMA foreign_keys = ON;