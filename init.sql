-- إعداد قاعدة البيانات الأولية
CREATE DATABASE IF NOT EXISTS daily_report CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE daily_report;

-- إعدادات إضافية لقاعدة البيانات
SET sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO';