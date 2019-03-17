SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE `log` (
  `chat_id` varchar(20) COLLATE utf8_bin NOT NULL,
  `message` text COLLATE utf8_bin NOT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

CREATE TABLE `message` (
  `chat_id` varchar(20) COLLATE utf8_bin NOT NULL,
  `user_id` varchar(20) COLLATE utf8_bin NOT NULL,
  `message_id` int(11) NOT NULL,
  `full_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `type` varchar(20) COLLATE utf8_bin NOT NULL,
  `text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `date` int(11) NOT NULL,
  `reply_to_message_id` varchar(20) COLLATE utf8_bin NOT NULL,
  `reply_to_user_id` varchar(20) COLLATE utf8_bin NOT NULL,
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
  `chat_id` varchar(20) COLLATE utf8_bin NOT NULL,
  `user_id` varchar(20) COLLATE utf8_bin NOT NULL,
  `type` varchar(20) COLLATE utf8_bin NOT NULL,
  `count` int(11) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;


ALTER TABLE `message_count`
  ADD PRIMARY KEY (`chat_id`,`user_id`,`type`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
