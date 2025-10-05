BEGIN TRANSACTION;

-- Agregar nuevos campos de función renal a la tabla guests
ALTER TABLE guests ADD COLUMN creatinina_serica REAL;
ALTER TABLE guests ADD COLUMN clearance_creatinina REAL;

CREATE INDEX IF NOT EXISTS idx_guests_sex_age ON guests(sex, age);

COMMIT;