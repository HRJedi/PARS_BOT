/* 
ЯДРО БОТА И STATE STORAGE
*/

CREATE TYPE "PARS_BOT".user_stat AS ENUM ('active', 'inactive', 'for delete');
CREATE TABLE "PARS_BOT".users
	("user_id" bigint PRIMARY KEY,
	"reg_date" timestamp NOT NULL DEFAULT now(),
	"f_name_tg" VARCHAR(50),
	"l_name_tg" VARCHAR(50),
	"username" VARCHAR(50),
	"f_name_real" VARCHAR(50),
	"l_name_real" VARCHAR(50),
	"tel_num" VARCHAR(50),
	"email" VARCHAR(100),
	"status" user_stat NOT NULL DEFAULT 'active');
	

CREATE TABLE "PARS_BOT".user_state
	("user_id" bigint PRIMARY KEY,
	"upd_date" timestamp NOT NULL DEFAULT now(),
	"state" VARCHAR(50) NOT NULL DEFAULT 'Инициализация',
	"addition" VARCHAR(50) NOT NULL DEFAULT 'ordinary',
	"user_message" TEXT);


CREATE TABLE "PARS_BOT".user_log
	("log_id" serial PRIMARY KEY,
	"event_date" timestamp NOT NULL DEFAULT now(),
	"user_id" bigint NOT NULL,
	"state" VARCHAR(50) NOT NULL DEFAULT 'Старт',
	"addition" VARCHAR(50) NOT NULL DEFAULT 'ordinary',
	"user_message" TEXT);



/* 
 * СТРУКТУРА
 * */


ALTER TABLE "PARS_BOT".user_state
ADD CONSTRAINT fk_state_users
	FOREIGN KEY
	(user_id) REFERENCES "PARS_BOT".users(user_id)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


ALTER TABLE "PARS_BOT".user_log
ADD CONSTRAINT fk_log_users
	FOREIGN KEY
	(user_id) REFERENCES "PARS_BOT".users(user_id)
	ON DELETE CASCADE
	ON UPDATE CASCADE;



/* 
 * ТРИГГЕРЫ БОТА
 * */


/* Добавить стейт после инициализации */
CREATE OR REPLACE FUNCTION user_insert_trigger_fnc()
RETURNS trigger AS
$$
BEGIN
INSERT INTO "PARS_BOT".user_state
	(user_id, upd_date, state, addition, user_message)
VALUES
	(NEW.user_id, now(), DEFAULT, DEFAULT, NULL)
ON CONFLICT
	(user_id)
DO UPDATE SET
	upd_date = EXCLUDED.upd_date,
	state = EXCLUDED.addition,
	addition = 'conlfict',
	user_message = EXCLUDED.user_message;
RETURN NEW;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER 
	user_insert_trigger
AFTER INSERT
ON 
	"PARS_BOT".users
FOR EACH ROW
EXECUTE PROCEDURE 
	user_insert_trigger_fnc();


/* Добавить лог после смены стейта */
CREATE OR REPLACE FUNCTION new_state_trigger_fnc()
RETURNS trigger AS
$$
BEGIN
INSERT INTO "PARS_BOT".user_log
	(user_id, state, addition, user_message)
VALUES
	(NEW.user_id, NEW.state, NEW.addition, NEW.user_message);
RETURN NEW;
END;
$$
LANGUAGE 'plpgsql';


CREATE TRIGGER 
	new_state_trigger
AFTER INSERT OR UPDATE
ON 
	"PARS_BOT".user_state
FOR EACH ROW
EXECUTE PROCEDURE 
	new_state_trigger_fnc();


/* 
Блок парсинга HH
*/

CREATE TABLE "PARS_BOT".user_req
	("user_id" bigint,
	"req_uuid" uuid PRIMARY KEY,
	"req_create" timestamp,
	"analysis_start" timestamp,
	"analysis_finish" timestamp,
	"archived" boolean DEFAULT False,
	"req_status" varchar(50) DEFAULT 'new reqest',
	"req_type" varchar(50) DEFAULT 'DEEP',
	"pars_source" varchar(50),
	"req_name" varchar(100),
	"total_time_sec" int);


CREATE TABLE "PARS_BOT".hh_req
	("req_uuid" uuid PRIMARY KEY,
	"date_from" DATE,
	"date_to" DATE,
	"search_field" varchar(50) DEFAULT 'ALL',
	"req_title" TEXT,
	"area" TEXT ARRAY DEFAULT '{All}',
	"industry" TEXT ARRAY DEFAULT '{All}',
    "employer_id" TEXT ARRAY DEFAULT '{All}',
    "experience" TEXT ARRAY DEFAULT '{All}',
    "employment" TEXT ARRAY DEFAULT '{All}',
    "schedule" TEXT ARRAY DEFAULT '{All}',
	"with_salary" boolean,
	"salary_cur" varchar(10),
	"prew_exept_count" int,
	"prew_vac_count" int,
	"prew_time_sec" int,
	"prew_complete" boolean,
	"deep_exept_count" int,
	"deep_vac_count" int,
	"deep_time_sec" int,
	"deep_complete" boolean);


CREATE TABLE "PARS_BOT".hh_vac_main
	("user_req_uuid" uuid,
	"vac_uuid" uuid PRIMARY KEY,
	"published_at" timestamp,
	"created_at" timestamp,
	"vac_id" bigint,
	"vac_link" VARCHAR(200),
	"vac_name" VARCHAR(150),
	"vac_name_tag" VARCHAR(100),
	"premium_vac" boolean,
	"region_name" VARCHAR(150),
	"city_name" VARCHAR(100),
	"salary_from" numeric,
	"salary_to" numeric,
	"salary_avg" numeric,
	"salary_cur" VARCHAR(10),
	"salary_type" VARCHAR(10),
	"employer_id" bigint,
	"employer_link" VARCHAR(200),
	"employer_name" VARCHAR(150),
	"it_accredited" boolean,
	"exp_criteria" VARCHAR(50),
	"schedule_type" VARCHAR(50),
	"employment_type" VARCHAR(50),
	"archived_vac" boolean,
    "accept_wo_cv" boolean,
	"with_test" boolean,
    "with_resp_letter" boolean);


CREATE TABLE "PARS_BOT".hh_vac_atr
	("vac_uuid" uuid PRIMARY KEY,
	"bill_type" VARCHAR(50),
    "branded_vac" boolean,
    "accept_for_invalid" boolean,
    "accept_for_kids" boolean,
    "accept_for_temp_w" boolean,
    "quick_responses_vac" boolean);
	

CREATE TABLE "PARS_BOT".hh_vac_desc
	("vac_uuid" uuid PRIMARY KEY,
	"desc" text);


CREATE TABLE "PARS_BOT".hh_vac_ks
	("vac_uuid" uuid,
	"key_skill" VARCHAR(150));


CREATE TABLE "PARS_BOT".hh_vac_roles
	("vac_uuid" uuid,
	"role" VARCHAR(150));


CREATE TABLE "PARS_BOT".hh_vac_langs
	("vac_uuid" uuid,
	"lang" VARCHAR(50));


CREATE TABLE "PARS_BOT".hh_vac_dl
	("vac_uuid" uuid,
	"dl_type" VARCHAR(10));


CREATE TABLE "PARS_BOT".hh_vac_empl
	("vac_uuid" uuid PRIMARY KEY,
	"empl_id" bigint,
	"type" VARCHAR(150));


CREATE TABLE "PARS_BOT".hh_empl_ind
	("vac_uuid" uuid,
	"empl_id" bigint,
	"industry" VARCHAR(250));



/* 
Блок парсинга HH - Ключи
*/

ALTER TABLE "PARS_BOT".user_req
ADD CONSTRAINT fk_ureq_users
	FOREIGN KEY
	(user_id) REFERENCES "PARS_BOT".users(user_id)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


ALTER TABLE "PARS_BOT".hh_req
ADD CONSTRAINT fk_hhreq_ureq
	FOREIGN KEY
	(req_uuid) REFERENCES "PARS_BOT".user_req(req_uuid)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


ALTER TABLE "PARS_BOT".hh_vac_main
ADD CONSTRAINT fk_main_ureq
	FOREIGN KEY
	(user_req_uuid) REFERENCES "PARS_BOT".user_req(req_uuid)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


ALTER TABLE "PARS_BOT".hh_vac_atr
ADD CONSTRAINT fk_atr_main
	FOREIGN KEY
	(vac_uuid) REFERENCES "PARS_BOT".hh_vac_main(vac_uuid)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


ALTER TABLE "PARS_BOT".hh_vac_desc
ADD CONSTRAINT fk_desc_main
	FOREIGN KEY
	(vac_uuid) REFERENCES "PARS_BOT".hh_vac_main(vac_uuid)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


ALTER TABLE "PARS_BOT".hh_vac_ks
ADD CONSTRAINT fk_ks_main
	FOREIGN KEY
	(vac_uuid) REFERENCES "PARS_BOT".hh_vac_main(vac_uuid)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


ALTER TABLE "PARS_BOT".hh_vac_roles
ADD CONSTRAINT fk_roles_main
	FOREIGN KEY
	(vac_uuid) REFERENCES "PARS_BOT".hh_vac_main(vac_uuid)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


ALTER TABLE "PARS_BOT".hh_vac_langs
ADD CONSTRAINT fk_langs_main
	FOREIGN KEY
	(vac_uuid) REFERENCES "PARS_BOT".hh_vac_main(vac_uuid)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


ALTER TABLE "PARS_BOT".hh_vac_dl
ADD CONSTRAINT fk_dl_main
	FOREIGN KEY
	(vac_uuid) REFERENCES "PARS_BOT".hh_vac_main(vac_uuid)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


ALTER TABLE "PARS_BOT".hh_vac_empl
ADD CONSTRAINT fk_empl_main
	FOREIGN KEY
	(vac_uuid) REFERENCES "PARS_BOT".hh_vac_main(vac_uuid)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


ALTER TABLE "PARS_BOT".hh_empl_ind
ADD CONSTRAINT fk_ind_empl
	FOREIGN KEY
	(vac_uuid) REFERENCES "PARS_BOT".hh_vac_empl(vac_uuid)
	ON DELETE CASCADE
	ON UPDATE CASCADE;


