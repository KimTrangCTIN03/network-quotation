from app.pages.bom import render_bom_page
from app.pages.calculation_results import render_calculation_results_page
from app.pages.auth import render_account_page, render_admin_page, render_login_page, render_register_page
from app.pages.dashboard import render_dashboard_page
from app.pages.pricing import render_pricing_page
from app.pages.quote import render_quote_page
from app.pages.survey import render_survey_page
from app.pages.topology import render_topology_page

__all__ = [
    "render_bom_page",
    "render_admin_page",
    "render_account_page",
    "render_calculation_results_page",
    "render_dashboard_page",
    "render_login_page",
    "render_register_page",
    "render_pricing_page",
    "render_quote_page",
    "render_survey_page",
    "render_topology_page",
]
