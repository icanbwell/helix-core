ALTER TABLE patient_access.metrics
ADD COLUMN partition_index INT DEFAULT NULL COMMENT 'Partition index',
ADD COLUMN chunk_index INT DEFAULT NULL COMMENT 'Chunk index',
ADD COLUMN partition_start_time DATETIME DEFAULT NULL COMMENT 'When did we start processing this batch',
ADD COLUMN chunk_start_time DATETIME DEFAULT NULL COMMENT 'When did we start processing this chunk';
