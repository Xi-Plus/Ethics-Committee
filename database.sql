SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `admins` (
  `chat_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `creator` tinyint(1) NOT NULL,
  `can_add_web_page_previews` tinyint(4) NOT NULL,
  `can_be_edited` tinyint(4) NOT NULL,
  `can_change_info` tinyint(4) NOT NULL,
  `can_delete_messages` tinyint(4) NOT NULL,
  `can_edit_messages` tinyint(4) NOT NULL,
  `can_invite_users` tinyint(4) NOT NULL,
  `can_pin_messages` tinyint(4) NOT NULL,
  `can_post_messages` tinyint(4) NOT NULL,
  `can_promote_members` tinyint(4) NOT NULL,
  `can_restrict_members` tinyint(4) NOT NULL,
  `can_send_media_messages` tinyint(4) NOT NULL,
  `can_send_messages` tinyint(4) NOT NULL,
  `can_send_other_messages` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
DELIMITER $$
CREATE TRIGGER `admins_add` AFTER INSERT ON `admins` FOR EACH ROW INSERT INTO `admins_changes` (`chat_id`, `user_id`, `action`, `can_add_web_page_previews`, `can_be_edited`, `can_change_info`, `can_delete_messages`, `can_edit_messages`, `can_invite_users`, `can_pin_messages`, `can_post_messages`, `can_promote_members`, `can_restrict_members`, `can_send_media_messages`, `can_send_messages`, `can_send_other_messages`) VALUES (
	NEW.`chat_id`, NEW.`user_id`, 'add',

	 NEW.`can_add_web_page_previews`,
	 NEW.`can_be_edited`,
	 NEW.`can_change_info`,
	 NEW.`can_delete_messages`,
	 NEW.`can_edit_messages`,
	 NEW.`can_invite_users`,
	 NEW.`can_pin_messages`,
	 NEW.`can_post_messages`,
	 NEW.`can_promote_members`,
	 NEW.`can_restrict_members`,
	 NEW.`can_send_media_messages`,
	 NEW.`can_send_messages`,
	 NEW.`can_send_other_messages`
	)
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `admins_remove` AFTER DELETE ON `admins` FOR EACH ROW INSERT INTO `admins_changes` (`chat_id`, `user_id`, `action`, `can_add_web_page_previews`, `can_be_edited`, `can_change_info`, `can_delete_messages`, `can_edit_messages`, `can_invite_users`, `can_pin_messages`, `can_post_messages`, `can_promote_members`, `can_restrict_members`, `can_send_media_messages`, `can_send_messages`, `can_send_other_messages`) VALUES (
	OLD.`chat_id`, OLD.`user_id`, 'remove',

	 OLD.`can_add_web_page_previews`,
	 OLD.`can_be_edited`,
	 OLD.`can_change_info`,
	 OLD.`can_delete_messages`,
	 OLD.`can_edit_messages`,
	 OLD.`can_invite_users`,
	 OLD.`can_pin_messages`,
	 OLD.`can_post_messages`,
	 OLD.`can_promote_members`,
	 OLD.`can_restrict_members`,
	 OLD.`can_send_media_messages`,
	 OLD.`can_send_messages`,
	 OLD.`can_send_other_messages`
	)
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `admins_update` AFTER UPDATE ON `admins` FOR EACH ROW INSERT INTO `admins_changes` (`chat_id`, `user_id`, `action`, `can_add_web_page_previews`, `can_be_edited`, `can_change_info`, `can_delete_messages`, `can_edit_messages`, `can_invite_users`, `can_pin_messages`, `can_post_messages`, `can_promote_members`, `can_restrict_members`, `can_send_media_messages`, `can_send_messages`, `can_send_other_messages`) VALUES (
	OLD.`chat_id`, OLD.`user_id`, 'update',

	IF (OLD.`can_add_web_page_previews` = NEW.`can_add_web_page_previews`, '',   CONCAT(OLD.`can_add_web_page_previews`, '->', NEW.`can_add_web_page_previews`)),
	IF (OLD.`can_be_edited` = NEW.`can_be_edited`, '',   CONCAT(OLD.`can_be_edited`, '->', NEW.`can_be_edited`)),
	IF (OLD.`can_change_info` = NEW.`can_change_info`, '',   CONCAT(OLD.`can_change_info`, '->', NEW.`can_change_info`)),
	IF (OLD.`can_delete_messages` = NEW.`can_delete_messages`, '',   CONCAT(OLD.`can_delete_messages`, '->', NEW.`can_delete_messages`)),
	IF (OLD.`can_edit_messages` = NEW.`can_edit_messages`, '',   CONCAT(OLD.`can_edit_messages`, '->', NEW.`can_edit_messages`)),
	IF (OLD.`can_invite_users` = NEW.`can_invite_users`, '',   CONCAT(OLD.`can_invite_users`, '->', NEW.`can_invite_users`)),
	IF (OLD.`can_pin_messages` = NEW.`can_pin_messages`, '',   CONCAT(OLD.`can_pin_messages`, '->', NEW.`can_pin_messages`)),
	IF (OLD.`can_post_messages` = NEW.`can_post_messages`, '',   CONCAT(OLD.`can_post_messages`, '->', NEW.`can_post_messages`)),
	IF (OLD.`can_promote_members` = NEW.`can_promote_members`, '',   CONCAT(OLD.`can_promote_members`, '->', NEW.`can_promote_members`)),
	IF (OLD.`can_restrict_members` = NEW.`can_restrict_members`, '',   CONCAT(OLD.`can_restrict_members`, '->', NEW.`can_restrict_members`)),
	IF (OLD.`can_send_media_messages` = NEW.`can_send_media_messages`, '',   CONCAT(OLD.`can_send_media_messages`, '->', NEW.`can_send_media_messages`)),
	IF (OLD.`can_send_messages` = NEW.`can_send_messages`, '',   CONCAT(OLD.`can_send_messages`, '->', NEW.`can_send_messages`)),
	IF (OLD.`can_send_other_messages` = NEW.`can_send_other_messages`, '',   CONCAT(OLD.`can_send_other_messages`, '->', NEW.`can_send_other_messages`))
	)
$$
DELIMITER ;

CREATE TABLE `admins_changes` (
  `chat_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `action` varchar(10) NOT NULL,
  `can_add_web_page_previews` varchar(5) NOT NULL,
  `can_be_edited` varchar(5) NOT NULL,
  `can_change_info` varchar(5) NOT NULL,
  `can_delete_messages` varchar(5) NOT NULL,
  `can_edit_messages` varchar(5) NOT NULL,
  `can_invite_users` varchar(5) NOT NULL,
  `can_pin_messages` varchar(5) NOT NULL,
  `can_post_messages` varchar(5) NOT NULL,
  `can_promote_members` varchar(5) NOT NULL,
  `can_restrict_members` varchar(5) NOT NULL,
  `can_send_media_messages` varchar(5) NOT NULL,
  `can_send_messages` varchar(5) NOT NULL,
  `can_send_other_messages` varchar(5) NOT NULL,
  `time` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

CREATE TABLE `group_name` (
  `chat_id` bigint(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `username` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

CREATE TABLE `group_setting` (
  `chat_id` bigint(20) DEFAULT NULL,
  `key` varchar(64) NOT NULL,
  `value` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

CREATE TABLE `log` (
  `log_id` int(11) NOT NULL,
  `chat_id` bigint(20) NOT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `time` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

CREATE TABLE `message` (
  `chat_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `message_id` int(11) NOT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `type` varchar(20) NOT NULL,
  `text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `date` int(11) NOT NULL,
  `reply_to_message_id` int(11) DEFAULT NULL,
  `reply_to_user_id` bigint(20) DEFAULT NULL,
  `time` timestamp NULL DEFAULT current_timestamp(),
  `deleted` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
DELIMITER $$
CREATE TRIGGER `count` AFTER INSERT ON `message` FOR EACH ROW BEGIN
INSERT INTO `message_count` (`chat_id`, `user_id`, `type`, `count`) VALUES (NEW.chat_id, NEW.user_id, NEW.type, 1)

ON DUPLICATE KEY UPDATE `count` = `count`+1, `updated_at` = CURRENT_TIMESTAMP;

END
$$
DELIMITER ;

CREATE TABLE `message_count` (
  `chat_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `type` varchar(20) NOT NULL,
  `count` int(11) NOT NULL DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

CREATE TABLE `permissions` (
  `chat_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  `user_right` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
DELIMITER $$
CREATE TRIGGER `permissions_change_add` AFTER INSERT ON `permissions` FOR EACH ROW INSERT INTO `permissions_changes`
(`chat_id`, `user_id`, `action`, `user_right`) VALUES (NEW.chat_id, NEW.user_id, 'add', NEW.user_right)
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `permissions_change_remove` AFTER DELETE ON `permissions` FOR EACH ROW INSERT INTO `permissions_changes`
(`chat_id`, `user_id`, `action`, `user_right`) VALUES (OLD.chat_id, OLD.user_id, 'remove', OLD.user_right)
$$
DELIMITER ;

CREATE TABLE `permissions_changes` (
  `chat_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) NOT NULL,
  `action` varchar(10) NOT NULL,
  `user_right` varchar(50) NOT NULL,
  `time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;

CREATE TABLE `user_name` (
  `user_id` bigint(20) NOT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `username` varchar(255) DEFAULT NULL,
  `comment` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
DELIMITER $$
CREATE TRIGGER `change_user_name` AFTER UPDATE ON `user_name` FOR EACH ROW BEGIN
INSERT INTO `user_name_changes` (`user_id`, `old_name`, `new_name`) VALUES (NEW.user_id, CONCAT( OLD.full_name," (",IFNULL(OLD.username, ''), ")"), CONCAT( NEW.full_name," (",IFNULL(NEW.username, ''), ")"));

END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `delete_user_name` AFTER DELETE ON `user_name` FOR EACH ROW BEGIN
INSERT INTO `user_name_changes` (`user_id`, `old_name`, `new_name`) VALUES (OLD.user_id, CONCAT( OLD.full_name," (",IFNULL(OLD.username, ''), ")"), '(deleted user)');

END
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `new_user_name` AFTER INSERT ON `user_name` FOR EACH ROW BEGIN
INSERT INTO `user_name_changes` (`user_id`, `old_name`, `new_name`) VALUES (NEW.user_id, "(new user)", CONCAT( NEW.full_name," (",IFNULL(NEW.username, ''), ")"));

END
$$
DELIMITER ;

CREATE TABLE `user_name_changes` (
  `user_id` bigint(20) NOT NULL,
  `old_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `new_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `time` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;


ALTER TABLE `admins`
  ADD PRIMARY KEY (`chat_id`,`user_id`);

ALTER TABLE `admins_changes`
  ADD KEY `time` (`time`);

ALTER TABLE `group_name`
  ADD PRIMARY KEY (`chat_id`);

ALTER TABLE `group_setting`
  ADD KEY `group_setting_ibfk_1` (`chat_id`);

ALTER TABLE `log`
  ADD PRIMARY KEY (`log_id`);

ALTER TABLE `message`
  ADD KEY `date` (`date`);

ALTER TABLE `message_count`
  ADD PRIMARY KEY (`chat_id`,`user_id`,`type`);

ALTER TABLE `permissions`
  ADD KEY `permissions_ibfk_1` (`chat_id`),
  ADD KEY `user_id` (`user_id`);

ALTER TABLE `user_name`
  ADD PRIMARY KEY (`user_id`);

ALTER TABLE `user_name_changes`
  ADD KEY `time` (`time`);


ALTER TABLE `log`
  MODIFY `log_id` int(11) NOT NULL AUTO_INCREMENT;


ALTER TABLE `admins`
  ADD CONSTRAINT `admins_ibfk_1` FOREIGN KEY (`chat_id`) REFERENCES `group_name` (`chat_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `group_setting`
  ADD CONSTRAINT `group_setting_ibfk_1` FOREIGN KEY (`chat_id`) REFERENCES `group_name` (`chat_id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `permissions`
  ADD CONSTRAINT `permissions_ibfk_1` FOREIGN KEY (`chat_id`) REFERENCES `group_name` (`chat_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
