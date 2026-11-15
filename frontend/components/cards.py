import streamlit as st

def render_stat_card(label: str, value: str, icon_str: str = "📊", caption: str = None, *args, **kwargs):
    """Renders a Canva-aligned statistics surface card with iconbox."""
    icon_svg = kwargs.get("icon_svg")
    icon_content = icon_svg if icon_svg else (icon_str if ("<svg" in str(icon_str) or "<span" in str(icon_str)) else f'<span style="font-size: 1.25rem;">{icon_str}</span>')
    caption_html = f'<div class="muted tiny mt-1" style="font-size: 0.78rem; color: #718a97; margin-top: 6px;">{caption}</div>' if caption else ""
    html = (
        '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 22px; padding: 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); min-height: 155px; display: flex; flex-direction: column; justify-content: space-between;">'
        f'<div style="width: 44px; height: 44px; border-radius: 12px; background: #eaf6f4; display: flex; align-items: center; justify-content: center; color: #087c76;">{icon_content}</div>'
        '<div>'
        f'<p style="color: #637d8c; font-size: 0.92rem; font-weight: 600; margin: 16px 0 4px 0;">{label}</p>'
        f'<div style="font-size: 2.35rem; font-weight: 800; color: #193648; letter-spacing: -0.03em; line-height: 1.05;">{value}</div>'
        f'{caption_html}'
        '</div>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def render_adherence_widget(recorded: int = 5, total: int = 7):
    """Renders the Canva medication adherence progress bar widget matching screenshot."""
    percentage = int((recorded / total) * 100) if total > 0 else 0
    html = (
        '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 22px; padding: 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); min-height: 310px; display: flex; flex-direction: column; justify-content: space-between;">'
        '<div>'
        '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 4px 0;">Medication adherence</h2>'
        '<p style="color: #637d8c; font-size: 0.85rem; margin: 0 0 28px 0;">Weekly adherence completion</p>'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">'
        '<span style="font-size: 0.95rem; font-weight: 600; color: #547382;">Recorded doses</span>'
        f'<strong style="font-size: 0.95rem; font-weight: 800; color: #193648;">{recorded} of {total}</strong>'
        '</div>'
        '<div style="height: 14px; background: #e6edf2; border-radius: 10px; overflow: hidden; margin-bottom: 22px;">'
        f'<div style="width: {percentage}%; height: 100%; background: #2ea294; border-radius: 10px; transition: width 0.4s ease;"></div>'
        '</div>'
        '</div>'
        '<p style="color: #718a97; font-size: 0.84rem; line-height: 1.5; margin: 0;">A visual summary of recorded actions, not clinical advice.</p>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def render_wellness_chart_svg():
    """Renders Canva 7-day Wellness Trend using lightweight SVG (No C-extensions/DLLs)."""
    html = (
        '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 22px; padding: 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); min-height: 310px;">'
        '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">'
        '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0;">Wellness trend</h2>'
        '<span style="background: #e9f4f8; color: #1b6d85; font-size: 0.78rem; font-weight: 700; padding: 4px 12px; border-radius: 20px;">7-Day Activity</span>'
        '</div>'
        '<p style="color: #637d8c; font-size: 0.85rem; margin: 0 0 16px 0;">Self-reported check-in score · last 7 days</p>'
        '<svg viewBox="0 0 520 215" style="width: 100%; height: auto; max-height: 230px; display: block; overflow: visible;">'
        '<defs>'
        '<linearGradient id="wellnessGrad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#dff2eb" stop-opacity="0.95"/>'
        '<stop offset="100%" stop-color="#e8f7f2" stop-opacity="0.7"/>'
        '</linearGradient>'
        '</defs>'
        '<line x1="32" y1="22" x2="495" y2="22" stroke="#f0f4f7" stroke-width="1.2"/>'
        '<line x1="32" y1="39" x2="495" y2="39" stroke="#f0f4f7" stroke-width="1.2"/>'
        '<line x1="32" y1="56" x2="495" y2="56" stroke="#f0f4f7" stroke-width="1.2"/>'
        '<line x1="32" y1="73" x2="495" y2="73" stroke="#f0f4f7" stroke-width="1.2"/>'
        '<line x1="32" y1="90" x2="495" y2="90" stroke="#f0f4f7" stroke-width="1.2"/>'
        '<line x1="32" y1="107" x2="495" y2="107" stroke="#f0f4f7" stroke-width="1.2"/>'
        '<line x1="32" y1="124" x2="495" y2="124" stroke="#f0f4f7" stroke-width="1.2"/>'
        '<line x1="32" y1="141" x2="495" y2="141" stroke="#f0f4f7" stroke-width="1.2"/>'
        '<line x1="32" y1="158" x2="495" y2="158" stroke="#f0f4f7" stroke-width="1.2"/>'
        '<line x1="32" y1="175" x2="495" y2="175" stroke="#f0f4f7" stroke-width="1.2"/>'
        '<text x="18" y="26" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">9</text>'
        '<text x="18" y="43" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">8</text>'
        '<text x="18" y="60" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">7</text>'
        '<text x="18" y="77" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">6</text>'
        '<text x="18" y="94" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">5</text>'
        '<text x="18" y="111" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">4</text>'
        '<text x="18" y="128" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">3</text>'
        '<text x="18" y="145" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">2</text>'
        '<text x="18" y="162" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">1</text>'
        '<text x="18" y="179" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">0</text>'
        '<path d="M 45 175 L 45 73 C 81.7 73, 81.7 56, 118.3 56 C 155 56, 155 73, 191.7 73 C 228.4 73, 228.4 39, 265 39 C 301.7 39, 301.7 56, 338.3 56 C 375 56, 375 39, 411.7 39 C 448.4 39, 448.4 22, 485 22 L 485 175 Z" fill="url(#wellnessGrad)" />'
        '<path d="M 45 73 C 81.7 73, 81.7 56, 118.3 56 C 155 56, 155 73, 191.7 73 C 228.4 73, 228.4 39, 265 39 C 301.7 39, 301.7 56, 338.3 56 C 375 56, 375 39, 411.7 39 C 448.4 39, 448.4 22, 485 22" fill="none" stroke="#0a837a" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
        '<circle cx="45" cy="73" r="4.5" fill="#FFFFFF" stroke="#0a837a" stroke-width="2.5"/>'
        '<circle cx="118.3" cy="56" r="4.5" fill="#FFFFFF" stroke="#0a837a" stroke-width="2.5"/>'
        '<circle cx="191.7" cy="73" r="4.5" fill="#FFFFFF" stroke="#0a837a" stroke-width="2.5"/>'
        '<circle cx="265" cy="39" r="4.5" fill="#FFFFFF" stroke="#0a837a" stroke-width="2.5"/>'
        '<circle cx="338.3" cy="56" r="4.5" fill="#FFFFFF" stroke="#0a837a" stroke-width="2.5"/>'
        '<circle cx="411.7" cy="39" r="4.5" fill="#FFFFFF" stroke="#0a837a" stroke-width="2.5"/>'
        '<circle cx="485" cy="22" r="4.5" fill="#FFFFFF" stroke="#0a837a" stroke-width="2.5"/>'
        '<text x="45" y="198" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">Sun</text>'
        '<text x="118.3" y="198" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">Mon</text>'
        '<text x="191.7" y="198" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">Tue</text>'
        '<text x="265" y="198" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">Wed</text>'
        '<text x="338.3" y="198" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">Thu</text>'
        '<text x="411.7" y="198" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">Fri</text>'
        '<text x="485" y="198" font-size="11" font-weight="600" fill="#718a97" text-anchor="middle">Sat</text>'
        '</svg>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def render_usage_chart_svg():
    """Renders Canva Admin Weekly Usage Bar Chart using lightweight SVG (No C-extensions/DLLs)."""
    html = (
        '<div style="background: #FFFFFF; border: 1px solid #dce9ef; border-radius: 20px; padding: 24px; box-shadow: 0 4px 20px rgba(24, 75, 103, 0.04); height: 100%;">'
        '<h2 style="font-size: 1.25rem; font-weight: 800; color: #193648; margin: 0 0 16px 0;">System usage activity</h2>'
        '<svg viewBox="0 0 520 230" style="width: 100%; height: auto; display: block;">'
        '<line x1="55" y1="20" x2="490" y2="20" stroke="#f0f5f7" stroke-width="1.2"/>'
        '<line x1="55" y1="42" x2="490" y2="42" stroke="#f0f5f7" stroke-width="1.2"/>'
        '<line x1="55" y1="64" x2="490" y2="64" stroke="#f0f5f7" stroke-width="1.2"/>'
        '<line x1="55" y1="86" x2="490" y2="86" stroke="#f0f5f7" stroke-width="1.2"/>'
        '<line x1="55" y1="108" x2="490" y2="108" stroke="#f0f5f7" stroke-width="1.2"/>'
        '<line x1="55" y1="130" x2="490" y2="130" stroke="#f0f5f7" stroke-width="1.2"/>'
        '<line x1="55" y1="152" x2="490" y2="152" stroke="#f0f5f7" stroke-width="1.2"/>'
        '<line x1="55" y1="174" x2="490" y2="174" stroke="#f0f5f7" stroke-width="1.2"/>'
        '<line x1="55" y1="196" x2="490" y2="196" stroke="#e6eef2" stroke-width="1.2"/>'
        '<text x="46" y="24" font-size="11" font-weight="600" fill="#7d95a2" text-anchor="end">1,600</text>'
        '<text x="46" y="46" font-size="11" font-weight="600" fill="#7d95a2" text-anchor="end">1,400</text>'
        '<text x="46" y="68" font-size="11" font-weight="600" fill="#7d95a2" text-anchor="end">1,200</text>'
        '<text x="46" y="90" font-size="11" font-weight="600" fill="#7d95a2" text-anchor="end">1,000</text>'
        '<text x="46" y="112" font-size="11" font-weight="600" fill="#7d95a2" text-anchor="end">800</text>'
        '<text x="46" y="134" font-size="11" font-weight="600" fill="#7d95a2" text-anchor="end">600</text>'
        '<text x="46" y="156" font-size="11" font-weight="600" fill="#7d95a2" text-anchor="end">400</text>'
        '<text x="46" y="178" font-size="11" font-weight="600" fill="#7d95a2" text-anchor="end">200</text>'
        '<text x="46" y="200" font-size="11" font-weight="600" fill="#7d95a2" text-anchor="end">0</text>'
        '<rect x="73" y="93" width="36" height="103" rx="7" ry="7" fill="#6ec2ab"/>'
        '<rect x="133" y="73" width="36" height="123" rx="7" ry="7" fill="#6ec2ab"/>'
        '<rect x="193" y="81" width="36" height="115" rx="7" ry="7" fill="#6ec2ab"/>'
        '<rect x="253" y="51" width="36" height="145" rx="7" ry="7" fill="#6ec2ab"/>'
        '<rect x="313" y="55" width="36" height="141" rx="7" ry="7" fill="#6ec2ab"/>'
        '<rect x="373" y="34" width="36" height="162" rx="7" ry="7" fill="#6ec2ab"/>'
        '<rect x="433" y="60" width="36" height="136" rx="7" ry="7" fill="#6ec2ab"/>'
        '<text x="91" y="218" font-size="12" font-weight="600" fill="#637d8c" text-anchor="middle">Mon</text>'
        '<text x="151" y="218" font-size="12" font-weight="600" fill="#637d8c" text-anchor="middle">Tue</text>'
        '<text x="211" y="218" font-size="12" font-weight="600" fill="#637d8c" text-anchor="middle">Wed</text>'
        '<text x="271" y="218" font-size="12" font-weight="600" fill="#637d8c" text-anchor="middle">Thu</text>'
        '<text x="331" y="218" font-size="12" font-weight="600" fill="#637d8c" text-anchor="middle">Fri</text>'
        '<text x="391" y="218" font-size="12" font-weight="600" fill="#637d8c" text-anchor="middle">Sat</text>'
        '<text x="451" y="218" font-size="12" font-weight="600" fill="#637d8c" text-anchor="middle">Sun</text>'
        '</svg>'
        '</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

def render_vital_pills(vitals: dict):
    """Renders a series of pill badges for patient health vitals."""
    pills_html = ""
    for label, val in vitals.items():
        if val:
            pills_html += f'<span class="badge badge-blue" style="margin-right: 8px; margin-bottom: 8px; font-size: 0.8rem;"><strong>{label}:</strong> {val}</span>'
    st.markdown(f'<div style="margin: 12px 0;">{pills_html}</div>', unsafe_allow_html=True)

def get_status_badge_html(status: str) -> str:
    """Returns a Canva-styled badge corresponding to normal, elevated, or low lab values."""
    status_clean = str(status).strip().upper()
    if status_clean in ["NORMAL", "OPTIMAL", "DESIRABLE", "REVIEWED"]:
        return '<span class="badge">Normal</span>'
    elif status_clean in ["HIGH", "ELEVATED", "CRITICAL HIGH"]:
        return '<span class="badge badge-amber">Elevated</span>'
    elif status_clean in ["LOW", "DEFICIENT", "CRITICAL LOW"]:
        return '<span class="badge badge-amber">Low</span>'
    elif status_clean in ["AVAILABLE", "INVITED"]:
        return '<span class="badge badge-blue">Available</span>'
    else:
        return f'<span class="badge">{status}</span>'
