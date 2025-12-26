from datetime import datetime
from app import db

# Association tables for many-to-many relationships (keeping for backward compatibility)
user_areas = db.Table('user_areas',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('area_id', db.Integer, db.ForeignKey('area.id'), primary_key=True)
)

user_stores = db.Table('user_stores',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('store_id', db.Integer, db.ForeignKey('store.id'), primary_key=True)
)

# Association tables for regions and branches (keeping for backward compatibility)
user_regions = db.Table('user_regions',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('region_id', db.Integer, db.ForeignKey('region.id'), primary_key=True)
)

user_branches = db.Table('user_branches',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('branch_id', db.Integer, db.ForeignKey('branch.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    employee_code = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Many-to-many relationships (keeping old for backward compatibility)
    assigned_areas = db.relationship('Area', secondary=user_areas, backref='users')
    assigned_stores = db.relationship('Store', secondary=user_stores, backref='users')
    
    # New relationships for regions and branches
    assigned_regions = db.relationship('Region', secondary=user_regions, backref='users')
    assigned_branches = db.relationship('Branch', secondary=user_branches, backref='users')
    
    # One-to-many relationship with reports
    reports = db.relationship('Report', backref='employee', lazy=True)

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    governorate = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    area = db.relationship('Area', backref='stores')

class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=True)
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # NULL for global regions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to owner
    owner = db.relationship('User', backref='owned_regions', foreign_keys=[owner_user_id])
    
    # Unique constraint: name must be unique per owner (NULL owner means global)
    __table_args__ = (db.UniqueConstraint('name', 'owner_user_id', name='unique_region_per_owner'),)

class Branch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=True)  # Can be NULL for standalone branches
    governorate = db.Column(db.String(100), nullable=True)  # Governorate field
    owner_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # NULL for global branches
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    region = db.relationship('Region', backref='branches')
    owner = db.relationship('User', backref='owned_branches', foreign_keys=[owner_user_id])
    
    # Unique constraint: code must be unique per owner (NULL owner means global)
    __table_args__ = (db.UniqueConstraint('code', 'owner_user_id', name='unique_branch_per_owner'),)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    report_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Report Status: new, under_review, reviewed, needs_revision
    status = db.Column(db.String(20), default='new', nullable=False)
    is_read = db.Column(db.Boolean, default=False)  # Track if admin has read the report
    
    # Sales Movement
    samsung_sales = db.Column(db.Text)
    competitors_sales = db.Column(db.Text)
    
    # Samsung Product Availability
    tv_availability = db.Column(db.Text)
    ha_availability = db.Column(db.Text)
    
    # Store Activities
    sfo_pmt = db.Column(db.Text)
    display_activities = db.Column(db.Text)
    sales_activities = db.Column(db.Text)
    store_issues = db.Column(db.Text)  # SDA, DOA
    
    # VOD
    vod_notes = db.Column(db.Text)
    
    # Store & Dealer's Situation
    complaints = db.Column(db.Text)
    issues = db.Column(db.Text)
    requirements = db.Column(db.Text)
    
    # Result & Action
    actions_taken = db.Column(db.Text)
    store_member_notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    store = db.relationship('Store', backref='reports')
    area = db.relationship('Area', backref='reports')
    comments = db.relationship('ReportComment', backref='report', lazy=True, cascade='all, delete-orphan')

class ReportComment(db.Model):
    """تعليقات الإدارة على التقارير"""
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Admin who commented
    comment_text = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)  # Track if SPVR has read the comment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    commenter = db.relationship('User', backref='comments_made', foreign_keys=[user_id])

class Notification(db.Model):
    """نظام الإشعارات"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # new_report, new_comment, status_change
    related_report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='notifications')
    related_report = db.relationship('Report', backref='notifications')

class AuditLog(db.Model):
    """سجل النشاطات الأمنية"""
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # login_success, login_failed, data_access, data_modification
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    details = db.Column(db.Text)  # JSON string with event details
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = db.relationship('User', backref='audit_logs')