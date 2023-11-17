-- Generate seats for each coach
CREATE OR REPLACE FUNCTION generate_seats()
RETURNS TRIGGER AS $$
DECLARE
    row_num INT;
    col_num INT;
BEGIN
    FOR row_num IN 1..NEW.row_number LOOP
        FOR col_num IN 1..NEW.column_number LOOP
            INSERT INTO qlxk_ghe (bien_so, row, col) VALUES (NEW.bien_so, row_num, col_num);
        END LOOP;
    END LOOP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_seats_trigger
AFTER INSERT ON qlxk_xe
FOR EACH ROW
EXECUTE FUNCTION generate_seats();

-- Generate tickets for each trips
CREATE OR REPLACE FUNCTION generate_tickets()
RETURNS TRIGGER AS $$
DECLARE
    ghe INT;
BEGIN
    FOR ghe IN (SELECT ghe_id FROM qlxk_ghe WHERE bien_so = NEW.bien_so) LOOP
        INSERT INTO qlxk_ve (ghe_id, chuyenxe_id, status) VALUES (ghe, NEW.chuyenxe_id, FALSE);
    END LOOP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_tickets_trigger
AFTER INSERT ON chuyenxe
FOR EACH ROW
EXECUTE FUNCTION generate_tickets();


