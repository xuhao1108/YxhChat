CREATE TRIGGER trigger_add_user AFTER INSERT ON `user` FOR EACH ROW
BEGIN
	INSERT INTO user_info ( user_id )
VALUES
	( new.user_id );
INSERT INTO user_friends ( user_id )
VALUES
	( new.user_id );
END;