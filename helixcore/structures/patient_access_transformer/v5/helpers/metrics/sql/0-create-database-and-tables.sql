CREATE SCHEMA IF NOT EXISTS `patient_access` DEFAULT CHARACTER SET utf8mb4 ;
USE `patient_access`;
-- patient_access.errors definition

CREATE TABLE `errors` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `run_id` varchar(255) NOT NULL COMMENT 'Flow run id in Prefect that created this row',
  `run_date_time` datetime NOT NULL COMMENT 'Flow run date time in Prefect that created this row',
  `connection_type` varchar(255) DEFAULT NULL COMMENT 'Type of connection: proa, hapi, hie',
  `fhir_version` varchar(255) DEFAULT NULL COMMENT 'FHIR version: r4, dstu2',
  `pipeline_category` varchar(255) DEFAULT NULL COMMENT 'Category of pipeline: Provider, Insurance',
  `pipeline_version` varchar(255) DEFAULT NULL COMMENT 'Version of helix.pipelines release',
  `new_tokens_only` tinyint(1) DEFAULT NULL COMMENT 'Whether we only want to use new tokens',
  `master_person_id` varchar(255) DEFAULT NULL COMMENT 'Master person id of the user whose patient record we are trying to retrieve',
  `client_person_id` varchar(255) DEFAULT NULL COMMENT 'Client person id of the user whose patient record we are trying to retrieve',
  `patient_id` varchar(255) DEFAULT NULL COMMENT 'Patient id in the source system',
  `client_source_url` varchar(255) DEFAULT NULL COMMENT 'Base url of the source system',
  `step` varchar(255) NOT NULL COMMENT 'Step in the process where the error occurred',
  `severity` varchar(255) NOT NULL COMMENT 'Severity of the error: fatal, error, warning, information',
  `source_system_type` varchar(255) DEFAULT NULL COMMENT 'Type of source system: Epic, Cerner, Athena, etc.',
  `created_date` datetime DEFAULT NULL COMMENT 'Date the token was created',
  `last_updated` datetime DEFAULT NULL COMMENT 'Date the token was last updated',
  `expiry` datetime DEFAULT NULL COMMENT 'Date the token expires',
  `scope` mediumtext COMMENT 'Scope of the token',
  `token` text COMMENT 'Token used to access the source system',
  `slug` varchar(255) DEFAULT NULL COMMENT 'Slug in b.well that identifies the source system',
  `resourceType` varchar(255) DEFAULT NULL COMMENT 'FHIR resourceType: Patient, Practitioner, Organization, Coverage, Observation',
  `request_id` varchar(255) DEFAULT NULL COMMENT 'Request id from b.well FHIR server if the error was sending data to our FHIR server',
  `resource_id` varchar(255) DEFAULT NULL COMMENT 'Resource id of the resource with the error',
  `url` text COMMENT 'Full url to retrieve this resource',
  `status_code` varchar(64) DEFAULT NULL COMMENT 'HTTP status code returned by the FHIR server',
  `error_text` mediumtext COMMENT 'Error text returned by the FHIR server',
  `raw_resource_json` longtext COMMENT 'JSON of the resource with the error',
  `resource_json` longtext COMMENT 'JSON of the resource with the error',
  PRIMARY KEY (`ID`),
  KEY `idx_errors_patient_id` (`patient_id`),
  KEY `idx_errors_run_date_time` (`run_date_time`),
  KEY `idx_errors_optimization` (`run_date_time`,`slug`,`patient_id`),
  KEY `idx_errors_run_id` (`run_id`),
  KEY `idx_run_id_run_date_time` (`run_id`,`run_date_time`),
  FULLTEXT KEY `idx_errors_error_text` (`error_text`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;


-- patient_access.match_errors definition

CREATE TABLE `match_errors` (
  `run_id` text NOT NULL,
  `run_date_time` timestamp NOT NULL,
  `connection_type` text,
  `fhir_version` text,
  `pipeline_category` text,
  `pipeline_version` text,
  `new_tokens_only` bit(1) DEFAULT NULL,
  `master_person_id` text,
  `slug` text,
  `patient_id` text,
  `client_person_id` text,
  `error` mediumtext,
  `client_person_to_patient_match` mediumtext,
  `client_person_to_patient_source` text,
  `client_person_to_patient_target` text,
  `master_person_to_client_person_source` text,
  `master_person_to_client_person_target` text,
  `master_person_to_client_person_match` mediumtext,
  `client_person_to_patient_diagnostics` mediumtext,
  `master_person_to_client_person_diagnostics` mediumtext,
  KEY `match_errors_run_id_IDX` (`run_id`(255),`run_date_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- patient_access.metrics definition

CREATE TABLE `metrics` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `run_id` varchar(255) NOT NULL COMMENT 'Flow run id in Prefect that created this row',
  `run_date_time` datetime NOT NULL COMMENT 'When was this flow run',
  `start_time` datetime NOT NULL COMMENT 'When did we start downloading this patient record',
  `end_time` datetime NOT NULL COMMENT 'When did we finish downloading this patient record',
  `connection_type` varchar(255) DEFAULT NULL COMMENT 'Type of connection: proa, hapi, hie',
  `fhir_version` varchar(255) DEFAULT NULL COMMENT 'FHIR version: r4, dstu2',
  `pipeline_category` varchar(255) DEFAULT NULL COMMENT 'Category of pipeline: Provider, Insurance',
  `pipeline_version` varchar(255) DEFAULT NULL COMMENT 'Version of helix.pipelines release',
  `new_tokens_only` tinyint(1) DEFAULT NULL COMMENT 'Whether we only want to use new tokens',
  `master_person_id` varchar(255) DEFAULT NULL COMMENT 'Master person id of the user whose patient record we are trying to retrieve',
  `client_person_id` varchar(255) DEFAULT NULL COMMENT 'Client person id of the user whose patient record we are trying to retrieve',
  `patient_id` varchar(255) DEFAULT NULL COMMENT 'Patient id in the source system',
  `source_system_type` varchar(255) DEFAULT NULL COMMENT 'Type of source system: Epic, Cerner, Athena, etc.',
  `created_date` datetime DEFAULT NULL COMMENT 'Date the token was created',
  `last_updated` datetime DEFAULT NULL COMMENT 'Date the token was last updated',
  `expiry` datetime DEFAULT NULL COMMENT 'Date the token expires',
  `scope` mediumtext,
  `slug` varchar(255) DEFAULT NULL COMMENT 'Slug in b.well that identifies the source system',
  `status` varchar(255) DEFAULT NULL COMMENT 'Status of the token',
  `token` text COMMENT 'Token used to access the source system',
  `url` text,
  `number_of_resources` int(11) NOT NULL COMMENT 'Number of resources successfully retrieved from the source system for this patient record',
  `error_count` int(11) NOT NULL COMMENT 'Number of errors encountered while retrieving this patient record',
  `warning_count` int(11) NOT NULL COMMENT 'Number of warnings encountered while retrieving this patient record',
  `time_to_get_resources_from_source` float DEFAULT NULL COMMENT 'Time in seconds to get resources from source system',
  `time_send_resources_to_fhir` float DEFAULT NULL COMMENT 'Time in seconds to send resources to b.well FHIR',
  `time_to_match_person` float DEFAULT NULL COMMENT 'Time in seconds to match person',
  `matched` tinyint(1) DEFAULT NULL COMMENT 'Whether the person was matched',
  PRIMARY KEY (`ID`),
  KEY `idx_metrics_patient_id` (`patient_id`),
  KEY `idx_metrics_patient_id_slug` (`patient_id`,`slug`),
  KEY `idx_client_slug_run` (`client_person_id`,`slug`,`run_date_time`),
  KEY `idx_run_id_run_date_time` (`run_id`,`run_date_time`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;


-- patient_access.raw_resource_metrics definition

CREATE TABLE `raw_resource_metrics` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `run_id` varchar(255) NOT NULL COMMENT 'Flow run id in Prefect that created this row',
  `run_date_time` datetime NOT NULL COMMENT 'When was this flow run',
  `connection_type` varchar(255) DEFAULT NULL COMMENT 'Type of connection: proa, hapi, hie',
  `fhir_version` varchar(255) DEFAULT NULL COMMENT 'FHIR version: r4, dstu2',
  `pipeline_category` varchar(255) DEFAULT NULL COMMENT 'Category of pipeline: Provider, Insurance',
  `pipeline_version` varchar(255) DEFAULT NULL COMMENT 'Version of helix.pipelines release',
  `new_tokens_only` tinyint(1) DEFAULT NULL COMMENT 'Whether we only want to use new tokens',
  `master_person_id` varchar(255) DEFAULT NULL COMMENT 'Master person id of the user whose patient record we are trying to retrieve',
  `client_person_id` varchar(255) DEFAULT NULL COMMENT 'Client person id of the user whose patient record we are trying to retrieve',
  `patient_id` varchar(255) DEFAULT NULL COMMENT 'Patient id in the source system',
  `source_system_type` varchar(255) DEFAULT NULL COMMENT 'Type of source system: Epic, Cerner, Athena, etc.',
  `scope` mediumtext COMMENT 'Scope of the token',
  `slug` varchar(255) DEFAULT NULL COMMENT 'Slug in b.well that identifies the source system',
  `url` text COMMENT 'url of the source system',
  `resource_type` varchar(255) DEFAULT NULL COMMENT 'Type of resource: Patient, Observation, etc.',
  `resource_count` int(11) DEFAULT NULL COMMENT 'Number of resources retrieved',
  `resource_urls` longtext COMMENT 'URLs of resources retrieved',
  `resource_text` longtext COMMENT 'JSON of resources retrieved',
  PRIMARY KEY (`ID`),
  KEY `idx_run_date_time` (`run_date_time`) USING BTREE,
  KEY `idx_raw_resource_metrics_run_id_patient_id` (`run_id`,`patient_id`),
  KEY `raw_resource_metrics_run_id_IDX` (`run_id`) USING BTREE,
  KEY `idx_run_id_run_date_time` (`run_id`,`run_date_time`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;


-- patient_access.resource_metrics definition

CREATE TABLE `resource_metrics` (
  `ID` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `run_id` varchar(255) NOT NULL COMMENT 'Flow run id in Prefect that created this row',
  `run_date_time` datetime NOT NULL COMMENT 'When was this flow run',
  `connection_type` varchar(255) DEFAULT NULL COMMENT 'Type of connection: proa, hapi, hie',
  `fhir_version` varchar(255) DEFAULT NULL COMMENT 'FHIR version: r4, dstu2',
  `pipeline_category` varchar(255) DEFAULT NULL COMMENT 'Category of pipeline: Provider, Insurance',
  `pipeline_version` varchar(255) DEFAULT NULL COMMENT 'Version of helix.pipelines release',
  `new_tokens_only` tinyint(1) DEFAULT NULL COMMENT 'Whether we only want to use new tokens',
  `master_person_id` varchar(255) DEFAULT NULL COMMENT 'Master person id of the user whose patient record we are trying to retrieve',
  `client_person_id` varchar(255) DEFAULT NULL COMMENT 'Client person id of the user whose patient record we are trying to retrieve',
  `patient_id` varchar(255) DEFAULT NULL COMMENT 'Patient id in the source system',
  `source_system_type` varchar(255) DEFAULT NULL COMMENT 'Type of source system: Epic, Cerner, Athena, etc.',
  `scope` mediumtext COMMENT 'Scope of the token',
  `slug` varchar(255) DEFAULT NULL COMMENT 'Slug in b.well that identifies the source system',
  `url` text COMMENT 'url of the source system',
  `resource_type` varchar(255) DEFAULT NULL COMMENT 'Type of resource: Patient, Observation, etc.',
  `resource_count` int(11) DEFAULT NULL COMMENT 'Number of resources retrieved',
  `resource_ids` text COMMENT 'resource ids retrieved',
  `resource_json` longtext COMMENT 'JSON of resources retrieved',
  PRIMARY KEY (`ID`),
  KEY `idx_resource_metrics_patient_id` (`patient_id`),
  KEY `idx_run_date_time` (`run_date_time`) USING BTREE,
  KEY `resource_metrics_master_person_id_IDX` (`master_person_id`,`run_date_time`) USING BTREE,
  KEY `resource_metrics_run_id_IDX` (`run_id`) USING BTREE,
  KEY `idx_run_id_run_date_time` (`run_id`,`run_date_time`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4;

