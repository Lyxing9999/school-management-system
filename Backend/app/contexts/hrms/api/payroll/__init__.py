


from app.contexts.hrms.api.payroll.payroll_command_routes import payroll_command_bp
from app.contexts.hrms.api.payroll.payroll_query_routes import payroll_query_bp
from app.contexts.hrms.api.payroll.audit_query_routes import audit_query_bp



def register_payroll_routes(app) -> None:
    app.register_blueprint(payroll_command_bp, url_prefix="/api/hrms")
    app.register_blueprint(payroll_query_bp, url_prefix="/api/hrms")
    app.register_blueprint(audit_query_bp, url_prefix="/api/hrms")
