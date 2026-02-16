USE facebookapi;



-- -----------------Users Table-------------------

CREATE TABLE user (
  id CHAR(36) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('admin','user') NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
);


CREATE TABLE friends (
  id CHAR(36) NOT NULL,
  sender_id CHAR(36) NULL,
  receiver_id CHAR(36) NULL,
  friend_status ENUM('pending','accepted','rejected') NOT NULL DEFAULT 'pending',

  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id),

  UNIQUE KEY unique_friends(sender_id, receiver_id),

  KEY friends(id),

  CONSTRAINT fk_user_sender
    FOREIGN KEY (sender_id) REFERENCES user(id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_user_receiver
    FOREIGN KEY (receiver_id) REFERENCES user(id)
    ON DELETE CASCADE ON UPDATE CASCADE
);


-- -----------------Refresh Tokens Table-------------------
CREATE TABLE refresh_token (
  id INT AUTO_INCREMENT PRIMARY KEY,
  token VARCHAR(500) NOT NULL UNIQUE,
  user_id CHAR(36) NOT NULL,
  is_revoked BOOLEAN NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  KEY index_refresh_user_id (user_id),

  CONSTRAINT fk_refresh_user
    FOREIGN KEY (user_id) REFERENCES `user`(id)
    ON DELETE CASCADE ON UPDATE CASCADE
);



CREATE TABLE audit_log (
  id CHAR(36) NOT NULL,
  action VARCHAR(255) NOT NULL,
  entity_id CHAR(36) NOT NULL,
  user_id CHAR(36) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id),

  KEY index_audit_entity_id (entity_id),
  KEY index_audit_user_id (user_id),
  KEY index_audit_action (action),

  CONSTRAINT fk_audit_user
    FOREIGN KEY (user_id) REFERENCES user(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);


SELECT * FROM user;
show create table user;
