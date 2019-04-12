SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `admins` (
  `chat_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `group_name` (
  `chat_id` bigint(20) NOT NULL,
  `title` varchar(255) COLLATE utf8_bin NOT NULL,
  `username` varchar(255) COLLATE utf8_bin DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `group_setting` (
  `chat_id` bigint(20) NOT NULL,
  `key` varchar(64) COLLATE utf8_bin NOT NULL,
  `value` mediumtext COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `log` (
  `chat_id` bigint(20) NOT NULL,
  `message` text COLLATE utf8_bin NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `message` (
  `chat_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `message_id` int(11) NOT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `type` varchar(20) COLLATE utf8_bin NOT NULL,
  `text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `date` int(11) NOT NULL,
  `reply_to_message_id` int(11) NOT NULL,
  `reply_to_user_id` int(11) NOT NULL,
  `time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
DELIMITER $$
CREATE TRIGGER `count` AFTER INSERT ON `message` FOR EACH ROW BEGIN
INSERT INTO `message_count` (`chat_id`, `user_id`, `type`, `count`) VALUES (NEW.chat_id, NEW.user_id, NEW.type, 1)

ON DUPLICATE KEY UPDATE `count` = `count`+1;

END
$$
DELIMITER ;

CREATE TABLE `message_count` (
  `chat_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `type` varchar(20) COLLATE utf8_bin NOT NULL,
  `count` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `permissions` (
  `chat_id` bigint(20) NOT NULL,
  `user_id` int(11) NOT NULL,
  `user_right` varchar(50) COLLATE utf8_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `user_name` (
  `user_id` int(11) NOT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `username` varchar(255) COLLATE utf8_bin NOT NULL DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

ALTER TABLE `admins`
  ADD PRIMARY KEY (`chat_id`,`user_id`);

ALTER TABLE `group_name`
  ADD PRIMARY KEY (`chat_id`);

ALTER TABLE `message_count`
  ADD PRIMARY KEY (`chat_id`,`user_id`,`type`);

ALTER TABLE `permissions`
  ADD PRIMARY KEY (`chat_id`,`user_id`,`user_right`);

ALTER TABLE `user_name`
  ADD PRIMARY KEY (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
