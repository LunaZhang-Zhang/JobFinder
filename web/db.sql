CREATE TABLE `user` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `favorite_job_ids` varchar(255) DEFAULT NULL,
  `created_time` datetime NOT NULL,
  `updated_time` datetime NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


CREATE TABLE `job` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `location` varchar(255) NOT NULL,
  `company` varchar(255) NOT NULL,
  `salary` varchar(255) NOT NULL,
  `min_salary` decimal(10,2) NOT NULL,
  `max_salary` decimal(10,2) NOT NULL,
  `salary_month` decimal(10,2) NOT NULL,
  `link` varchar(4096) NOT NULL,
  `background` varchar(255) NOT NULL,
  `requirements` varchar(4096) NOT NULL,
  `created_time` datetime NOT NULL,
  `updated_time` datetime NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

ALTER TABLE user ADD UNIQUE KEY(username);
