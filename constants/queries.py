CREATE_FAVORITE = "CREATE TABLE favorite(id INT, lectures TEXT, PRIMARY KEY (id))"
IF_CREATE_FAVORITE = "CREATE TABLE IF NOT EXISTS favorite(id INT, lectures TEXT, PRIMARY KEY (id))"
IF_DROP_FAVORITE = "DROP TABLE IF EXISTS favorite"
INSERT_FAVORITE = "INSERT INTO favorite(id, lectures) VALUES({0}, '{1}')"
DROP_FAVORITE = "DROP TABLE favorite"
SELECT_ALL_FAVORITE = "SELECT * FROM favorite"
SELECT_BY_ID_FAVORITE = "SELECT lectures FROM favorite WHERE id = {0}"
UPDATE_FAVORITE = "UPDATE favorite SET lectures = '{1}' WHERE id = {0}"
EXISTS_FAVORITE = "SELECT EXISTS(SELECT id FROM favorite WHERE id = {0})"
DELETE_FAVORITE = "DELETE FROM favorite WHERE id = {0}"


CREATE_PARTICIPANTS = "CREATE TABLE participants(id INT, username TEXT, fullname TEXT," \
                      "job TEXT, interests TEXT, active BIT, photo TEXT, PRIMARY KEY(id))"
IF_CREATE_PARTICIPANTS = "CREATE TABLE IF NOT EXISTS participants(id INT, username TEXT, fullname TEXT," \
                         "job TEXT, interests TEXT, active BIT, photo TEXT, PRIMARY KEY(id))"
IF_DROP_PARTICIPANTS = "DROP TABLE IF EXISTS participants"
DROP_PARTICIPANTS = "DROP TABLE participants"
SELECT_ALL_PARTICIPANTS = "SELECT * FROM participants"
INSERT_PARTICIPANTS = "INSERT INTO participants(id, username, fullname, job, interests, active, photo) " \
                      "VALUES({0}, '{1}', '{2}', '{3}', '{4}', {5}, '{6}')"
SELECT_BY_ID_PARTICIPANTS = "SELECT username, fullname, job, interests, active, photo " \
                            "FROM participants WHERE id = {0}"
UPDATE_PARTICIPANTS = "UPDATE participants SET username = '{1}', fullname = '{2}', job = '{3}', interests = '{4}', " \
                      "active = {5}, photo = '{6}' WHERE id = {0}"
EXISTS_PARTICIPANTS = "SELECT EXISTS(SELECT id FROM participants WHERE id = {0})"
DELETE_PARTICIPANTS = "DELETE FROM participants WHERE id = {0}"
SELECT_ALL_IDS_PARTICIPANTS = "SELECT id FROM participants"
SELECT_POSSIBLE_IDS_PARTICIPANTS = "SELECT id FROM participants WHERE id != {0}"


CREATE_ESTIMATES = "CREATE TABLE estimates(id INT, summ INT, num INT, PRIMARY KEY (id))"
IF_CREATE_ESTIMATES = "CREATE TABLE IF NOT EXISTS estimates(id INT, summ INT, num INT, PRIMARY KEY (id))"
IF_DROP_ESTIMATES = "DROP TABLE IF EXISTS estimates"
DROP_ESTIMATES = "DROP TABLE estimates"
SELECT_BY_ID_ESTIMATES = "SELECT summ, num FROM estimates WHERE id = {0}"
INSERT_ESTIMATES = "INSERT INTO estimates(id, summ, num) VALUES({0}, {1}, {2})"
UPDATE_ESTIMATES = "UPDATE estimates SET summ = {1}, num = {2} WHERE id = {0}"
