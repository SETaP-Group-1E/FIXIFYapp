-- SQLite
SELECT * FROM job ORDER BY created_at DESC;

SELECT COUNT(*) AS total_jobs FROM job;

SELECT * FROM job 
WHERE DATE(created_at) = DATE('now');

SELECT title, budget, is_negotiable 
FROM job 
WHERE budget IS NOT NULL 
ORDER BY budget DESC;

-- Get all cleaning jobs sorted by urgency
SELECT title, description, urgency, location 
FROM job 
WHERE category = 'Cleaning'
ORDER BY 
  CASE urgency 
    WHEN 'High' THEN 1 
    WHEN 'Medium' THEN 2 
    ELSE 3 
  END;

ALTER TABLE job ADD COLUMN status VARCHAR(20) DEFAULT 'pending';
-- Run incase you run into a value error mentioning job_status not being present
