from flask import render_template, request, redirect, url_for, session, flash, jsonify
from app.employee import bp
from app.models import User, Area, Store, Report, Region, Branch, db
from functools import wraps
from datetime import datetime
import pytz
from zoneinfo import ZoneInfo

# Timezone utilities for Egypt (Africa/Cairo) with automatic DST handling
def get_egypt_timezone():
    """Get Egypt timezone with automatic DST handling"""
    try:
        # Use zoneinfo (Python 3.9+) for better timezone handling
        return ZoneInfo("Africa/Cairo")
    except:
        # Fallback to pytz for older Python versions
        return pytz.timezone('Africa/Cairo')

def utc_to_egypt_time(utc_datetime):
    """Convert UTC datetime to Egypt local time with DST handling"""
    if utc_datetime is None:
        return None
    
    # Ensure the datetime is timezone-aware (UTC)
    if utc_datetime.tzinfo is None:
        utc_datetime = utc_datetime.replace(tzinfo=pytz.UTC)
    
    # Convert to Egypt timezone
    egypt_tz = get_egypt_timezone()
    return utc_datetime.astimezone(egypt_tz)

def parse_date_filter(date_str, is_end_date=False):
    """Parse date filter with proper timezone handling"""
    if not date_str:
        return None
    
    try:
        # Parse the date string (YYYY-MM-DD format from HTML date input)
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        if is_end_date:
            # For end date, set to end of day (23:59:59) in Egypt timezone
            parsed_date = parsed_date.replace(hour=23, minute=59, second=59)
        else:
            # For start date, set to beginning of day (00:00:00) in Egypt timezone
            parsed_date = parsed_date.replace(hour=0, minute=0, second=0)
        
        # Convert Egypt local time to UTC for database query
        egypt_tz = get_egypt_timezone()
        
        try:
            # Try zoneinfo first (Python 3.9+)
            egypt_datetime = parsed_date.replace(tzinfo=egypt_tz)
        except:
            # Fallback to pytz
            egypt_tz = pytz.timezone('Africa/Cairo')
            egypt_datetime = egypt_tz.localize(parsed_date)
        
        # Convert to UTC and remove timezone info for database
        return egypt_datetime.astimezone(pytz.UTC).replace(tzinfo=None)
        
    except ValueError:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    # Get recent reports ordered by creation date (most recent first)
    recent_reports_raw = Report.query.filter_by(user_id=user.id).order_by(Report.created_at.desc()).limit(5).all()
    
    # Convert timestamps to Egypt local time for display
    recent_reports = []
    for report in recent_reports_raw:
        # Create a copy of the report data with converted timestamps
        report_data = {
            'id': report.id,
            'store': report.store,
            'area': report.area,
            'report_date': utc_to_egypt_time(report.report_date) if report.report_date else None,
            'created_at': utc_to_egypt_time(report.created_at) if report.created_at else None,
            'original_report': report  # Keep reference to original report if needed
        }
        recent_reports.append(report_data)
    
    return render_template('employee/dashboard.html', user=user, recent_reports=recent_reports)

@bp.route('/report', methods=['GET', 'POST'])
@login_required
def create_report():
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        try:
            print(f"📝 POST request received from user {user.employee_name}")
            print(f"📋 Form data keys: {list(request.form.keys())}")
            
            # Get form data - now using branch instead of area/store
            branch_id = request.form.get('branch_id')
            print(f"🏢 Branch ID received: {branch_id}")
            
            if not branch_id:
                print("❌ No branch_id provided")
                flash('Please select a shop.', 'error')
                return redirect(url_for('employee.create_report'))
            
            # Get branch and create area/store if needed for backward compatibility
            branch = Branch.query.get(branch_id)
            if not branch:
                print(f"❌ Shop with ID {branch_id} not found")
                flash('Invalid shop selected.', 'error')
                return redirect(url_for('employee.create_report'))
            
            print(f"✅ Branch found: {branch.name} ({branch.code})")
            
            # Check if shop belongs to current user
            if branch.owner_user_id != user.id:
                print(f"❌ Shop belongs to user {branch.owner_user_id}, not {user.id}")
                flash('You do not have access to this shop.', 'error')
                return redirect(url_for('employee.create_report'))
            
            # For backward compatibility, we'll create a temporary area and store
            # or use existing ones based on branch name/code
            region_name = branch.region.name if branch.region else 'Default Region'
            area = Area.query.filter_by(name=region_name).first()
            if not area:
                area = Area(name=region_name)
                db.session.add(area)
                db.session.flush()
            
            store = Store.query.filter_by(code=branch.code).first()
            if not store:
                store = Store(name=branch.name, code=branch.code, area_id=area.id)
                db.session.add(store)
                db.session.flush()
            else:
                # Update store name and area if branch info has changed
                if store.name != branch.name:
                    store.name = branch.name
                if store.area_id != area.id:
                    store.area_id = area.id
            
            area_id = area.id
            store_id = store.id
            
            # Sales Movement
            samsung_sales = request.form.get('samsung_sales', '')
            competitors_sales = request.form.get('competitors_sales', '')
            
            # Samsung Product Availability
            tv_availability = request.form.get('tv_availability', '')
            ha_availability = request.form.get('ha_availability', '')
            
            # Store Activities
            sfo_pmt = request.form.get('sfo_pmt', '')
            display_activities = request.form.get('display_activities', '')
            store_issues = request.form.get('store_issues', '')
            
            # VOD
            vod_notes = request.form.get('vod_notes', '')
            
            # Store & Dealer's Situation
            complaints = request.form.get('complaints', '')
            issues = request.form.get('issues', '')
            requirements = request.form.get('requirements', '')
            
            # Result & Action
            actions_taken = request.form.get('actions_taken', '')
            store_member_notes = request.form.get('store_member_notes', '')
            
            # Create report
            report = Report(
                user_id=user.id,
                area_id=area_id,
                store_id=store_id,
                samsung_sales=samsung_sales,
                competitors_sales=competitors_sales,
                tv_availability=tv_availability,
                ha_availability=ha_availability,
                sfo_pmt=sfo_pmt,
                display_activities=display_activities,
                store_issues=store_issues,
                vod_notes=vod_notes,
                complaints=complaints,
                issues=issues,
                requirements=requirements,
                actions_taken=actions_taken,
                store_member_notes=store_member_notes
            )
            
            print(f"💾 Saving report for branch: {branch.name}")
            db.session.add(report)
            db.session.commit()
            
            print(f"✅ Report saved successfully with ID: {report.id}")
            flash('Report submitted successfully!', 'success')
            return redirect(url_for('employee.dashboard'))
            
        except Exception as e:
            print(f"❌ Error saving report: {str(e)}")
            db.session.rollback()
            flash(f'Error submitting report: {str(e)}', 'error')
            return redirect(url_for('employee.create_report'))
    
    return render_template('employee/report_form.html', user=user)

@bp.route('/batch-reports', methods=['GET'])
@login_required
def batch_reports():
    """صفحة إنشاء تقارير متعددة"""
    user = User.query.get(session['user_id'])
    return render_template('employee/batch_reports.html', user=user)

@bp.route('/submit-batch-reports', methods=['POST'])
@login_required
def submit_batch_reports():
    """معالجة إرسال التقارير المتعددة"""
    user = User.query.get(session['user_id'])
    
    try:
        data = request.get_json()
        reports_data = data.get('reports', [])
        report_date_str = data.get('report_date', '')
        
        if not reports_data:
            return jsonify({'success': False, 'message': 'No reports provided'})
        
        print(f"📝 Batch submission from user {user.employee_name}")
        print(f"📋 Number of reports: {len(reports_data)}")
        
        # Parse report date
        report_date = None
        if report_date_str:
            try:
                report_date = datetime.fromisoformat(report_date_str.replace('T', ' '))
            except:
                report_date = datetime.utcnow()
        else:
            report_date = datetime.utcnow()
        
        created_reports = []
        
        for i, report_data in enumerate(reports_data):
            branch_id = report_data.get('branch_id')
            
            if not branch_id:
                return jsonify({'success': False, 'message': f'No shop selected for report {i+1}'})
            
            # Get branch and validate ownership
            branch = Branch.query.get(branch_id)
            if not branch:
                return jsonify({'success': False, 'message': f'Invalid shop for report {i+1}'})
            
            if branch.owner_user_id != user.id:
                return jsonify({'success': False, 'message': f'You do not have access to shop in report {i+1}'})
            
            # Create area and store for backward compatibility
            region_name = branch.region.name if branch.region else 'Default Region'
            area = Area.query.filter_by(name=region_name).first()
            if not area:
                area = Area(name=region_name)
                db.session.add(area)
                db.session.flush()
            
            store = Store.query.filter_by(code=branch.code).first()
            if not store:
                store = Store(name=branch.name, code=branch.code, area_id=area.id)
                db.session.add(store)
                db.session.flush()
            else:
                if store.name != branch.name:
                    store.name = branch.name
                if store.area_id != area.id:
                    store.area_id = area.id
            
            # Create report
            report = Report(
                user_id=user.id,
                area_id=area.id,
                store_id=store.id,
                report_date=report_date,
                samsung_sales=report_data.get('samsung_sales', ''),
                competitors_sales=report_data.get('competitors_sales', ''),
                tv_availability=report_data.get('tv_availability', ''),
                ha_availability=report_data.get('ha_availability', ''),
                sfo_pmt=report_data.get('sfo_pmt', ''),
                display_activities=report_data.get('display_activities', ''),
                store_issues=report_data.get('store_issues', ''),
                complaints=report_data.get('complaints', ''),
                issues=report_data.get('issues', ''),
                requirements=report_data.get('requirements', ''),
                actions_taken=report_data.get('actions_taken', ''),
                store_member_notes=report_data.get('store_member_notes', '')
            )
            
            db.session.add(report)
            created_reports.append(report)
        
        db.session.commit()
        
        print(f"✅ Successfully created {len(created_reports)} reports")
        
        return jsonify({
            'success': True, 
            'message': f'Successfully submitted {len(created_reports)} reports',
            'count': len(created_reports)
        })
        
    except Exception as e:
        print(f"❌ Error in batch submission: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error submitting reports: {str(e)}'})

@bp.route('/test-report')
@login_required
def test_report():
    """صفحة اختبار مبسطة لإنشاء التقارير"""
    user = User.query.get(session['user_id'])
    return render_template('employee/test_report_form.html', user=user)



@bp.route('/api/branches/<int:region_id>')
@login_required
def get_branches_by_region(region_id):
    user = User.query.get(session['user_id'])
    
    # Get branches in the region that are owned by the user
    branches = Branch.query.filter(
        Branch.region_id == region_id,
        Branch.owner_user_id == user.id
    ).all()
    
    branches_data = [{'id': branch.id, 'name': branch.name, 'code': branch.code} for branch in branches]
    return jsonify(branches_data)



@bp.route('/api/search_branches')
@login_required
def search_branches():
    user = User.query.get(session['user_id'])
    query = request.args.get('q', '').strip()
    
    # If no query, return all user's branches (for initial load)
    if not query:
        branches = Branch.query.filter(
            Branch.owner_user_id == user.id
        ).order_by(Branch.name).limit(20).all()
    else:
        # Search in user's branches only - support both name and code search
        branches = Branch.query.filter(
            db.or_(
                Branch.name.ilike(f'%{query}%'),
                Branch.code.ilike(f'%{query}%')
            ),
            Branch.owner_user_id == user.id
        ).order_by(Branch.name).limit(15).all()
    
    branches_data = [{'id': branch.id, 'name': branch.name, 'code': branch.code, 'region': branch.region.name if branch.region else 'No Region'} for branch in branches]
    return jsonify(branches_data)

@bp.route('/my_reports')
@login_required
def my_reports():
    """View user's own reports with filtering"""
    user = User.query.get(session['user_id'])
    
    # Get filter parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    store_name = request.args.get('store_name', '')
    
    # Build query
    query = Report.query.filter_by(user_id=user.id).join(Store)
    
    # Fixed date filtering with proper timezone handling
    if start_date:
        start_datetime = parse_date_filter(start_date, is_end_date=False)
        if start_datetime:
            query = query.filter(Report.report_date >= start_datetime)
    
    if end_date:
        end_datetime = parse_date_filter(end_date, is_end_date=True)
        if end_datetime:
            query = query.filter(Report.report_date <= end_datetime)
    
    if store_name:
        query = query.filter(Store.name.contains(store_name))
    
    reports = query.order_by(Report.created_at.desc()).all()
    
    return render_template('employee/my_reports.html', reports=reports, user=user)

@bp.route('/report_preview/<int:report_id>')
@login_required
def report_preview(report_id):
    """Preview report content in a modal/popup"""
    user = User.query.get(session['user_id'])
    report = Report.query.get_or_404(report_id)
    
    # Check if user has access to this report (either their own or admin)
    if not session.get('is_admin') and report.user_id != user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('employee.dashboard'))
    
    return render_template('employee/report_preview.html', report=report)

@bp.route('/api/my_reports')
@login_required
def api_my_reports():
    """API endpoint for SPVR's own reports"""
    user = User.query.get(session['user_id'])
    
    # Get filter parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    store_name = request.args.get('store_name', '')
    
    # Build query
    query = Report.query.filter_by(user_id=user.id).join(Store)
    
    # Fixed date filtering with proper timezone handling
    if start_date:
        start_datetime = parse_date_filter(start_date, is_end_date=False)
        if start_datetime:
            query = query.filter(Report.report_date >= start_datetime)
    
    if end_date:
        end_datetime = parse_date_filter(end_date, is_end_date=True)
        if end_datetime:
            query = query.filter(Report.report_date <= end_datetime)
    
    if store_name:
        query = query.filter(Store.name.contains(store_name))
    
    reports = query.order_by(Report.created_at.desc()).all()
    
    reports_data = []
    for report in reports:
        # Convert UTC times to Egypt local time for display
        report_date_local = utc_to_egypt_time(report.report_date)
        created_at_local = utc_to_egypt_time(report.created_at)
        
        reports_data.append({
            'id': report.id,
            'store_name': report.store.name,
            'store_code': report.store.code,
            'area': report.area.name,
            'report_date': report_date_local.strftime('%Y-%m-%d %H:%M') if report_date_local else '',
            'created_at': created_at_local.strftime('%Y-%m-%d %H:%M') if created_at_local else ''
        })
    
    return jsonify(reports_data)

@bp.route('/view_reports')
@login_required
def view_reports():
    """View reports page with filtering capabilities"""
    user = User.query.get(session['user_id'])
    
    # Get user's branches for the branch filter
    user_branches = Branch.query.filter_by(owner_user_id=user.id).order_by(Branch.name).all()
    
    return render_template('employee/view_reports.html', user=user, branches=user_branches)

@bp.route('/api/view_reports')
@login_required
def api_view_reports():
    """API endpoint for filtered reports view"""
    user = User.query.get(session['user_id'])
    
    # Get filter parameters
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    branch_id = request.args.get('branch_id', '')
    
    # Build query - join with Store and Branch to get branch information
    query = Report.query.filter_by(user_id=user.id).join(Store).join(Area)
    
    # Date filtering with proper timezone handling
    if start_date:
        start_datetime = parse_date_filter(start_date, is_end_date=False)
        if start_datetime:
            query = query.filter(Report.report_date >= start_datetime)
    
    if end_date:
        end_datetime = parse_date_filter(end_date, is_end_date=True)
        if end_datetime:
            query = query.filter(Report.report_date <= end_datetime)
    
    # Branch filtering - match by store code with branch code
    if branch_id:
        branch = Branch.query.get(branch_id)
        if branch and branch.owner_user_id == user.id:
            query = query.filter(Store.code == branch.code)
    
    reports = query.order_by(Report.created_at.desc()).all()
    
    reports_data = []
    for report in reports:
        # Convert UTC times to Egypt local time for display
        report_date_local = utc_to_egypt_time(report.report_date)
        created_at_local = utc_to_egypt_time(report.created_at)
        
        # Find the branch for this report
        branch_name = ''
        branch = Branch.query.filter_by(code=report.store.code, owner_user_id=user.id).first()
        if branch:
            branch_name = branch.name
        
        reports_data.append({
            'id': report.id,
            'store_name': report.store.name,
            'store_code': report.store.code,
            'area': report.area.name,
            'branch_name': branch_name,
            'spvr_name': report.employee.employee_name,
            'report_date': report_date_local.strftime('%Y-%m-%d') if report_date_local else 'N/A',
            'report_time': report_date_local.strftime('%H:%M') if report_date_local else 'N/A',
            'created_at': created_at_local.strftime('%Y-%m-%d %H:%M') if created_at_local else 'N/A',
            'submitted_time': created_at_local.strftime('%H:%M') if created_at_local else 'N/A'
        })
    
    return jsonify(reports_data)

@bp.route('/view_report/<int:report_id>')
@login_required
def view_report_detail(report_id):
    """View detailed report in read-only mode"""
    user = User.query.get(session['user_id'])
    report = Report.query.get_or_404(report_id)
    
    # Check if user has access to this report
    if report.user_id != user.id:
        flash('Access denied. You can only view your own reports.', 'error')
        return redirect(url_for('employee.view_reports'))
    
    # Find the branch for this report
    branch = Branch.query.filter_by(code=report.store.code, owner_user_id=user.id).first()
    
    # Convert UTC time to Egypt local time
    report.submitted_time_egypt = utc_to_egypt_time(report.created_at)
    
    return render_template('employee/view_report_detail.html', report=report, user=user, branch=branch)


# ============================================================================
# NOTIFICATIONS & COMMENTS FOR EMPLOYEES
# ============================================================================

@bp.route('/api/notifications', methods=['GET'])
@login_required
def api_get_notifications():
    """Get notifications for current user"""
    try:
        from app.models import Notification
        
        user = User.query.get(session['user_id'])
        notifications = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).limit(20).all()
        
        notifications_data = []
        for notif in notifications:
            notif_time_egypt = utc_to_egypt_time(notif.created_at)
            notifications_data.append({
                'id': notif.id,
                'title': notif.title,
                'message': notif.message,
                'type': notif.notification_type,
                'is_read': notif.is_read,
                'related_report_id': notif.related_report_id,
                'created_at': notif_time_egypt.strftime('%Y-%m-%d %H:%M') if notif_time_egypt else ''
            })
        
        return jsonify({
            'success': True,
            'notifications': notifications_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/notifications/unread-count', methods=['GET'])
@login_required
def api_get_unread_count():
    """Get count of unread notifications"""
    try:
        from app.models import Notification
        
        user = User.query.get(session['user_id'])
        unread_count = Notification.query.filter_by(user_id=user.id, is_read=False).count()
        
        return jsonify({
            'success': True,
            'unread_count': unread_count
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@login_required
def api_mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        from app.models import Notification
        
        user = User.query.get(session['user_id'])
        notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first_or_404()
        
        notification.is_read = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/notifications/mark-all-read', methods=['PUT'])
@login_required
def api_mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        from app.models import Notification
        
        user = User.query.get(session['user_id'])
        Notification.query.filter_by(user_id=user.id, is_read=False).update({'is_read': True})
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'All notifications marked as read'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/reports/<int:report_id>/comments', methods=['GET'])
@login_required
def api_get_report_comments(report_id):
    """Get comments for a report (employee view)"""
    try:
        from app.models import ReportComment
        
        user = User.query.get(session['user_id'])
        report = Report.query.get_or_404(report_id)
        
        # Check if user owns this report
        if report.user_id != user.id:
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        comments = ReportComment.query.filter_by(report_id=report_id).order_by(ReportComment.created_at.asc()).all()
        
        comments_data = []
        for comment in comments:
            comment_time_egypt = utc_to_egypt_time(comment.created_at)
            comments_data.append({
                'id': comment.id,
                'comment_text': comment.comment_text,
                'commenter_name': comment.commenter.employee_name,
                'is_read': comment.is_read,
                'created_at': comment_time_egypt.strftime('%Y-%m-%d %H:%M') if comment_time_egypt else ''
            })
            
            # Mark comment as read
            if not comment.is_read:
                comment.is_read = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'comments': comments_data,
            'report_status': report.status
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/notifications')
@login_required
def notifications_page():
    """صفحة الإشعارات"""
    user = User.query.get(session['user_id'])
    return render_template('employee/notifications.html', user=user)
