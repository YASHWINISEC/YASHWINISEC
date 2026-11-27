#!/usr/bin/env python3
# Auto-generates the full burgundy GitHub Profile SVG suite and README.md
# from profile.json, plus fetches LIVE GitHub contribution calendar data
# via GitHub's GraphQL API when GITHUB_TOKEN is available.
# Zero third-party dependencies — uses only the Python 3 standard library.

import datetime
import html
import json
import math
import os
import urllib.parse
import urllib.request

SERIF = "Georgia, 'Times New Roman', 'DejaVu Serif', serif"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace"

PALETTE = ["#1C0A13", "#451126", "#701A3D", "#C77B9B", "#E5B5C7"]


def esc(text):
    return html.escape(str(text), quote=True)


def badge_part(text):
    t = str(text).replace("-", "--").replace("_", "__")
    return urllib.parse.quote(t, safe="")


def write_file(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")


def fetch_live_contributions(username):
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        return None

    query = '''
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
                contributionLevel
              }
            }
          }
        }
      }
    }
    '''
    payload = json.dumps({"query": query, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": f"{username}-profile-generator",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        weeks = cal["weeks"][-52:]
        level_map = {
            "NONE": 0,
            "FIRST_QUARTILE": 1,
            "SECOND_QUARTILE": 2,
            "THIRD_QUARTILE": 3,
            "FOURTH_QUARTILE": 4,
        }
        all_days = []
        grid = []
        for w in weeks:
            col_levels = []
            for d in w["contributionDays"]:
                cnt = int(d["contributionCount"])
                lvl = level_map.get(d["contributionLevel"], 0)
                col_levels.append(lvl)
                all_days.append((d["date"], cnt))
            grid.append(col_levels)

        active_days = sum(1 for _, c in all_days if c > 0)
        longest_streak = 0
        current_run = 0
        best_day = 0
        for _, c in all_days:
            if c > best_day:
                best_day = c
            if c > 0:
                current_run += 1
                if current_run > longest_streak:
                    longest_streak = current_run
            else:
                current_run = 0

        return {
            "live": True,
            "total": int(cal["totalContributions"]),
            "active_days": active_days,
            "longest_streak": longest_streak,
            "best_day": best_day,
            "grid": grid,
            "updated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%d %b %Y"),
        }
    except Exception as e:
        print(f"Live GraphQL fetch skipped ({e}); using preview mode.")
        return None


def build_about_svg(cfg):
    ident = cfg["identity"]
    lines = cfg["about_terminal"]
    term_rows = []
    y = 26
    for row in lines[:5]:
        key = esc(row["key"]).ljust(11)
        val = esc(row["value"])
        term_rows.append(
            f'        <text x="0" y="{y}" fill="#E5B5C7" xml:space="preserve">  {key} <tspan fill="#701A3D">→</tspan> <tspan fill="#F8F0F3">{val}</tspan></text>'
        )
        y += 24

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 350" width="1200" height="350" role="img" aria-labelledby="ym-s1-title ym-s1-desc">
  <title id="ym-s1-title">01 About — Hello, I'm {esc(ident["first_name"])}.</title>
  <desc id="ym-s1-desc">Burgundy editorial about section with terminal profile and verified engineering focus for {esc(ident["name"])}.</desc>
  <defs>
    <linearGradient id="ym-s1-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10070C" />
      <stop offset="55%" stop-color="#190B12" />
      <stop offset="100%" stop-color="#2E0B1A">
        <animate attributeName="stop-color" values="#2E0B1A;#3F1024;#2E0B1A" dur="12s" repeatCount="indefinite" />
      </stop>
    </linearGradient>
    <linearGradient id="ym-s1-term-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#160910" />
      <stop offset="100%" stop-color="#270A16" />
    </linearGradient>
    <linearGradient id="ym-s1-line" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#C77B9B" stop-opacity="0.9" />
      <stop offset="45%" stop-color="#701A3D" stop-opacity="0.55" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0.1" />
    </linearGradient>
    <linearGradient id="ym-s1-border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#701A3D" stop-opacity="0.8" />
      <stop offset="50%" stop-color="#C77B9B" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0.8" />
    </linearGradient>
    <clipPath id="ym-s1-clip"><rect x="1" y="1" width="1198" height="348" rx="16" /></clipPath>
  </defs>

  <g clip-path="url(#ym-s1-clip)">
    <rect width="1200" height="350" fill="url(#ym-s1-bg)" />

    <g transform="translate(42, 42)">
      <text x="0" y="0" font-family="{MONO}" font-size="11" font-weight="700" fill="#C77B9B" letter-spacing="2">01  ABOUT</text>
      <text x="0" y="34" font-family="{SERIF}" font-size="30" font-weight="700" fill="#F8F0F3">Hello, I'm {esc(ident["first_name"])}.</text>
      <text x="1116" y="28" text-anchor="end" font-family="{MONO}" font-size="11" fill="#C77B9B" fill-opacity="0.8" letter-spacing="1.4">{esc(ident["role_line"].upper())}</text>
      <rect x="0" y="48" width="1116" height="1.5" fill="url(#ym-s1-line)" />
    </g>

    <g transform="translate(42, 112)">
      <rect x="0" y="0" width="764" height="206" rx="12" fill="url(#ym-s1-term-bg)" stroke="#701A3D" stroke-width="1.2" />
      <path d="M 1 12 Q 1 1 12 1 L 752 1 Q 763 1 763 12 L 763 34 L 1 34 Z" fill="#451126" fill-opacity="0.55" />
      <circle cx="20" cy="18" r="5" fill="#C77B9B" fill-opacity="0.85" />
      <circle cx="37" cy="18" r="5" fill="#701A3D" />
      <circle cx="54" cy="18" r="5" fill="#451126" stroke="#C77B9B" stroke-width="0.8" />
      <text x="382" y="22" text-anchor="middle" font-family="{MONO}" font-size="11" fill="#E5B5C7" fill-opacity="0.85">{esc(ident["first_name"].lower())}@portfolio ~</text>

      <g transform="translate(22, 62)" font-family="{MONO}" font-size="12.5">
        <text x="0" y="0" fill="#C77B9B">$ <tspan fill="#F8F0F3">whoami</tspan></text>
{chr(10).join(term_rows)}
        <rect x="612" y="110" width="8" height="14" fill="#E5B5C7">
          <animate attributeName="opacity" values="1;0;1" dur="1.1s" repeatCount="indefinite" />
        </rect>
      </g>
    </g>

    <g transform="translate(826, 112)">
      <rect x="0" y="0" width="332" height="96" rx="12" fill="#1E0913" stroke="#701A3D" stroke-width="1.1" />
      <text x="20" y="26" font-family="{MONO}" font-size="10.5" fill="#C77B9B" letter-spacing="1.5">PRIMARY LANGUAGE</text>
      <text x="20" y="58" font-family="{SERIF}" font-size="26" font-weight="700" fill="#F8F0F3">{esc(ident["primary_language"])}</text>
      <text x="20" y="80" font-family="{MONO}" font-size="11" fill="#E5B5C7" fill-opacity="0.85">{esc(ident["primary_stack_note"])}</text>

      <rect x="0" y="110" width="332" height="96" rx="12" fill="#1E0913" stroke="#701A3D" stroke-width="1.1" />
      <text x="20" y="136" font-family="{MONO}" font-size="10.5" fill="#C77B9B" letter-spacing="1.5">CURRENTLY EXPLORING</text>
      <text x="20" y="166" font-family="{SERIF}" font-size="22" font-weight="700" fill="#F8F0F3">{esc(ident["currently_exploring_title"])}</text>
      <text x="20" y="188" font-family="{MONO}" font-size="11" fill="#E5B5C7" fill-opacity="0.85">{esc(ident["currently_exploring_note"])}</text>
    </g>

    <rect x="1" y="1" width="1198" height="348" rx="16" fill="none" stroke="url(#ym-s1-border)" stroke-width="1.3" />
  </g>
</svg>'''


def build_experience_svg(cfg):
    exp = cfg["experience"]
    p = exp["primary"]
    s = exp["secondary"]
    strip = exp["credentials_strip"]

    def render_tags(tags, stroke_col, stroke_op="0.45"):
        out = []
        tx = 0
        for t in tags[:5]:
            tw = max(66, len(t) * 8 + 22)
            out.append(f'<rect x="{tx}" y="0" width="{tw}" height="22" rx="6" fill="#190B12" fill-opacity="0.7" stroke="{stroke_col}" stroke-opacity="{stroke_op}" />')
            out.append(f'<text x="{tx + tw/2:.1f}" y="14.5" text-anchor="middle" fill="#E5B5C7">{esc(t)}</text>')
            tx += tw + 8
        return "".join(out)

    p_bullets = []
    by = 96
    for h in p["highlights"][:2]:
        p_bullets.append(
            f'      <text x="24" y="{by}" font-family="{SANS}" font-size="12.8" fill="#F8F0F3" fill-opacity="0.94">'
            f'<tspan font-weight="700" fill="#E5B5C7">• {esc(h["label"])}</tspan> {esc(h["detail"])}</text>'
        )
        by += 24

    strip_xml = []
    col_x = [0, 308, 612, 894]
    div_x = [286, 590, 872]
    for i, item in enumerate(strip[:4]):
        if i > 0:
            strip_xml.append(f'      <line x1="{div_x[i-1]}" y1="14" x2="{div_x[i-1]}" y2="82" stroke="#451126" stroke-width="1" />')
        unit_span = f' <tspan font-size="13" font-family="{MONO}" fill="#E5B5C7">{esc(item["unit"])}</tspan>' if item.get("unit") else ""
        strip_xml.append(
            f'''      <g transform="translate({col_x[i]}, 18)">
        <text x="0" y="10" font-family="{MONO}" font-size="10" fill="#C77B9B" letter-spacing="1.4">{esc(item["label"])}</text>
        <text x="0" y="42" font-family="{SERIF}" font-size="26" font-weight="700" fill="#F8F0F3">{esc(item["big"])}{unit_span}</text>
        <text x="0" y="62" font-family="{SANS}" font-size="11.5" fill="#C77B9B">{esc(item["sub"])}</text>
      </g>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 410" width="1200" height="410" role="img" aria-labelledby="ym-s2-title ym-s2-desc">
  <title id="ym-s2-title">02 Experience &amp; Recognition — Proof, on the record.</title>
  <desc id="ym-s2-desc">Verified internships and academic credentials.</desc>
  <defs>
    <linearGradient id="ym-s2-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10070C" />
      <stop offset="50%" stop-color="#190B12" />
      <stop offset="100%" stop-color="#360D1E" />
    </linearGradient>
    <linearGradient id="ym-s2-card-p" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#290B18" />
      <stop offset="100%" stop-color="#4A1229">
        <animate attributeName="stop-color" values="#4A1229;#5E1734;#4A1229" dur="10s" repeatCount="indefinite" />
      </stop>
    </linearGradient>
    <linearGradient id="ym-s2-card-s" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1F0913" />
      <stop offset="100%" stop-color="#3A0F21" />
    </linearGradient>
    <linearGradient id="ym-s2-line" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#C77B9B" stop-opacity="0.9" />
      <stop offset="50%" stop-color="#701A3D" stop-opacity="0.5" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0.1" />
    </linearGradient>
    <linearGradient id="ym-s2-border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#701A3D" stop-opacity="0.8" />
      <stop offset="50%" stop-color="#C77B9B" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0.85" />
    </linearGradient>
    <clipPath id="ym-s2-clip"><rect x="1" y="1" width="1198" height="408" rx="16" /></clipPath>
  </defs>

  <g clip-path="url(#ym-s2-clip)">
    <rect width="1200" height="410" fill="url(#ym-s2-bg)" />

    <g transform="translate(42, 42)">
      <text x="0" y="0" font-family="{MONO}" font-size="11" font-weight="700" fill="#C77B9B" letter-spacing="2">02  EXPERIENCE &amp; RECOGNITION</text>
      <text x="0" y="34" font-family="{SERIF}" font-size="30" font-weight="700" fill="#F8F0F3">Proof, on the record.</text>
      <text x="1116" y="28" text-anchor="end" font-family="{MONO}" font-size="11" fill="#C77B9B" fill-opacity="0.8" letter-spacing="1.4">INTERNSHIPS · ACADEMICS · ENGINEERING</text>
      <rect x="0" y="48" width="1116" height="1.5" fill="url(#ym-s2-line)" />
    </g>

    <g transform="translate(42, 110)">
      <rect x="0" y="0" width="636" height="176" rx="14" fill="url(#ym-s2-card-p)" stroke="#C77B9B" stroke-opacity="0.55" stroke-width="1.2" />
      <text x="616" y="102" text-anchor="end" font-family="{SERIF}" font-size="86" font-weight="700" fill="#E5B5C7" fill-opacity="0.09" letter-spacing="4">{esc(p["watermark"])}</text>
      <text x="24" y="30" font-family="{MONO}" font-size="10.5" fill="#E5B5C7" letter-spacing="1.6">{esc(p["company"].upper())} · {esc(p["period"])}</text>
      <text x="24" y="64" font-family="{SERIF}" font-size="25" font-weight="700" fill="#F8F0F3">{esc(p["role"])}</text>
{chr(10).join(p_bullets)}
      <g transform="translate(24, 138)" font-family="{MONO}" font-size="10">{render_tags(p["tags"], "#C77B9B", "0.45")}</g>
    </g>

    <g transform="translate(696, 110)">
      <rect x="0" y="0" width="462" height="176" rx="14" fill="url(#ym-s2-card-s)" stroke="#701A3D" stroke-width="1.2" />
      <text x="442" y="100" text-anchor="end" font-family="{SERIF}" font-size="76" font-weight="700" fill="#E5B5C7" fill-opacity="0.08">{esc(s["watermark"])}</text>
      <text x="24" y="30" font-family="{MONO}" font-size="10.5" fill="#C77B9B" letter-spacing="1.6">{esc(s["company"].upper())} · {esc(s["period"])}</text>
      <text x="24" y="64" font-family="{SERIF}" font-size="24" font-weight="700" fill="#F8F0F3">{esc(s["role"])}</text>
      <text x="24" y="96" font-family="{SANS}" font-size="12.8" fill="#E5B5C7" fill-opacity="0.92">{esc(s["summary_line1"])}</text>
      <text x="24" y="118" font-family="{SANS}" font-size="12.8" fill="#E5B5C7" fill-opacity="0.92">{esc(s["summary_line2"])}</text>
      <g transform="translate(24, 138)" font-family="{MONO}" font-size="10">{render_tags(s["tags"], "#701A3D", "0.85")}</g>
    </g>

    <g transform="translate(42, 304)">
      <line x1="0" y1="0" x2="1116" y2="0" stroke="#451126" stroke-width="1" />
{chr(10).join(strip_xml)}
    </g>

    <rect x="1" y="1" width="1198" height="408" rx="16" fill="none" stroke="url(#ym-s2-border)" stroke-width="1.3" />
  </g>
</svg>'''


def build_section_header(prefix, eyebrow, title, right_tag):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 104" width="1200" height="104" role="img" aria-label="{esc(eyebrow)} — {esc(title)}">
  <defs>
    <linearGradient id="{prefix}-bg" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#10070C" />
      <stop offset="60%" stop-color="#1D0913" />
      <stop offset="100%" stop-color="#360D1E" />
    </linearGradient>
    <linearGradient id="{prefix}-line" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#E5B5C7" stop-opacity="0.95" />
      <stop offset="50%" stop-color="#701A3D" stop-opacity="0.6" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0.1" />
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="1198" height="102" rx="14" fill="url(#{prefix}-bg)" stroke="#451126" stroke-width="1.2" />
  <g transform="translate(42, 34)">
    <text x="0" y="0" font-family="{MONO}" font-size="11" font-weight="700" fill="#C77B9B" letter-spacing="2">{esc(eyebrow)}</text>
    <text x="0" y="36" font-family="{SERIF}" font-size="30" font-weight="700" fill="#F8F0F3">{esc(title)}</text>
    <text x="1116" y="30" text-anchor="end" font-family="{MONO}" font-size="11" fill="#C77B9B" letter-spacing="1.4">{esc(right_tag)}</text>
    <rect x="0" y="50" width="1116" height="1.5" fill="url(#{prefix}-line)" />
  </g>
</svg>'''


def build_project_card(idx, proj):
    prefix = f"ym-p{idx}"
    pill_xml = []
    px = 0
    for p in proj["pills"][:7]:
        pw = max(68, len(p) * 8 + 22)
        if px + pw > 760:
            break
        pill_xml.append(f'<rect x="{px}" y="0" width="{pw}" height="24" rx="6" fill="#16080F" stroke="#701A3D" stroke-width="1" />')
        pill_xml.append(f'<text x="{px + pw/2:.1f}" y="15.5" text-anchor="middle" fill="#E5B5C7">{esc(p)}</text>')
        px += pw + 8

    node_xml = []
    ny = 28
    flow = proj["flow"][:3]
    for i, node in enumerate(flow):
        node_xml.append(f'<rect x="0" y="{ny}" width="316" height="42" rx="8" fill="#14070D" fill-opacity="0.88" stroke="#701A3D" stroke-width="1" />')
        node_xml.append(f'<circle cx="16" cy="{ny+21}" r="3.5" fill="#E5B5C7" />')
        node_xml.append(f'<text x="30" y="{ny+18}" font-family="{MONO}" font-size="10.5" font-weight="700" fill="#F8F0F3">{esc(node["step"])}</text>')
        node_xml.append(f'<text x="30" y="{ny+33}" font-family="{SANS}" font-size="10.5" fill="#C77B9B">{esc(node["note"])}</text>')
        if i < len(flow) - 1:
            node_xml.append(f'<line x1="158" y1="{ny+42}" x2="158" y2="{ny+54}" stroke="#C77B9B" stroke-width="1.2" stroke-opacity="0.7" />')
        ny += 54

    accent_end = proj.get("accent_end", "#4A1229")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 248" width="1200" height="248" role="img" aria-label="{esc(proj["title"])} — {esc(proj["subtitle"])}">
  <defs>
    <linearGradient id="{prefix}-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#12070D" />
      <stop offset="55%" stop-color="#1D0913" />
      <stop offset="100%" stop-color="{esc(accent_end)}" />
    </linearGradient>
    <linearGradient id="{prefix}-border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#C77B9B" stop-opacity="0.6" />
      <stop offset="50%" stop-color="#701A3D" stop-opacity="0.55" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0.85" />
    </linearGradient>
    <linearGradient id="{prefix}-sweep" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#701A3D" stop-opacity="0" />
      <stop offset="50%" stop-color="#E5B5C7" stop-opacity="0.85" />
      <stop offset="100%" stop-color="#701A3D" stop-opacity="0" />
    </linearGradient>
    <clipPath id="{prefix}-clip"><rect x="1" y="1" width="1198" height="246" rx="14" /></clipPath>
  </defs>

  <g clip-path="url(#{prefix}-clip)">
    <rect width="1200" height="248" fill="url(#{prefix}-bg)" />
    <line x1="20" y1="2" x2="1180" y2="2" stroke="url(#{prefix}-sweep)" stroke-width="2" stroke-dasharray="180 980" stroke-dashoffset="0">
      <animate attributeName="stroke-dashoffset" from="1160" to="0" dur="8s" repeatCount="indefinite" />
    </line>

    <g transform="translate(42, 40)">
      <text x="0" y="0" font-family="{MONO}" font-size="11" font-weight="700" fill="#C77B9B" letter-spacing="1.8">{esc(proj["eyebrow"])}</text>
      <text x="0" y="42" font-family="{SERIF}" font-size="31" font-weight="700" fill="#F8F0F3">{esc(proj["title"])}</text>
      <text x="0" y="68" font-family="{SANS}" font-size="14" font-weight="600" fill="#E5B5C7">{esc(proj["subtitle"])}</text>
      <text x="0" y="102" font-family="{SANS}" font-size="13.5" fill="#F8F0F3" fill-opacity="0.88">{esc(proj["desc1"])}</text>
      <text x="0" y="124" font-family="{SANS}" font-size="13.5" fill="#F8F0F3" fill-opacity="0.88">{esc(proj["desc2"])}</text>
      <g transform="translate(0, 154)" font-family="{MONO}" font-size="10.5">{"".join(pill_xml)}</g>
    </g>

    <g transform="translate(838, 16)">
      <text x="0" y="16" font-family="{MONO}" font-size="10" fill="#C77B9B" letter-spacing="1.5">ARCHITECTURE FLOW</text>
      {"".join(node_xml)}
    </g>

    <rect x="1" y="1" width="1198" height="246" rx="14" fill="none" stroke="url(#{prefix}-border)" stroke-width="1.3" />
  </g>
</svg>'''


def build_skills_svg(cfg):
    skills = cfg["skills"][:6]
    cards_xml = []
    for i, sk in enumerate(skills):
        col = i % 3
        row = i // 3
        x = 42 + col * 378
        y = 110 + row * 134
        stroke = '#C77B9B" stroke-opacity="0.55' if sk.get("highlight") else '#701A3D'
        tag_col = "#E5B5C7" if sk.get("highlight") else "#C77B9B"
        cards_xml.append(
            f'''    <g transform="translate({x}, {y})">
      <rect x="0" y="0" width="360" height="118" rx="12" fill="url(#ym-s4-card)" stroke="{stroke}" stroke-width="1.15" />
      <text x="20" y="26" font-family="{MONO}" font-size="10.5" fill="{tag_col}" letter-spacing="1.4">{esc(sk["tag"])}</text>
      <text x="20" y="60" font-family="{SERIF}" font-size="21" font-weight="700" fill="#F8F0F3">{esc(sk["headline"])}</text>
      <text x="20" y="84" font-family="{SANS}" font-size="13" font-weight="600" fill="#E5B5C7">{esc(sk["sub"])}</text>
      <text x="20" y="104" font-family="{MONO}" font-size="10" fill="#C77B9B">{esc(sk["footer"])}</text>
    </g>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 390" width="1200" height="390" role="img" aria-labelledby="ym-s4-title ym-s4-desc">
  <title id="ym-s4-title">04 Technical Stack — Tools of the craft.</title>
  <desc id="ym-s4-desc">Six-card burgundy bento grid of verified technologies, auto-generated from profile.json.</desc>
  <defs>
    <linearGradient id="ym-s4-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10070C" />
      <stop offset="50%" stop-color="#190B12" />
      <stop offset="100%" stop-color="#360D1E" />
    </linearGradient>
    <linearGradient id="ym-s4-card" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1E0913" />
      <stop offset="100%" stop-color="#310C1C" />
    </linearGradient>
    <linearGradient id="ym-s4-line" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#C77B9B" stop-opacity="0.9" />
      <stop offset="50%" stop-color="#701A3D" stop-opacity="0.55" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0.1" />
    </linearGradient>
    <linearGradient id="ym-s4-border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#701A3D" stop-opacity="0.8" />
      <stop offset="50%" stop-color="#C77B9B" stop-opacity="0.35" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0.85" />
    </linearGradient>
    <clipPath id="ym-s4-clip"><rect x="1" y="1" width="1198" height="388" rx="16" /></clipPath>
  </defs>

  <g clip-path="url(#ym-s4-clip)">
    <rect width="1200" height="390" fill="url(#ym-s4-bg)" />

    <g transform="translate(42, 42)">
      <text x="0" y="0" font-family="{MONO}" font-size="11" font-weight="700" fill="#C77B9B" letter-spacing="2">04  TECHNICAL STACK</text>
      <text x="0" y="34" font-family="{SERIF}" font-size="30" font-weight="700" fill="#F8F0F3">Tools of the craft.</text>
      <text x="1116" y="28" text-anchor="end" font-family="{MONO}" font-size="11" fill="#C77B9B" letter-spacing="1.4">SYNCED FROM PROFILE.JSON</text>
      <rect x="0" y="48" width="1116" height="1.5" fill="url(#ym-s4-line)" />
    </g>

{chr(10).join(cards_xml)}

    <rect x="1" y="1" width="1198" height="388" rx="16" fill="none" stroke="url(#ym-s4-border)" stroke-width="1.3" />
  </g>
</svg>'''


def build_activity_svg(cfg, live_data):
    username = cfg["identity"]["username"]
    cells = []

    if live_data and live_data.get("live"):
        right_label = f"REAL DATA · REFRESHED {live_data['updated_at'].upper()}"
        sub_label = f"COMMIT LOG · LIVE GITHUB ACTIVITY (@{username})"
        footer_note = f"Source: live GitHub contribution calendar for @{username} · updated automatically via GitHub Actions"
        metrics_xml = f'''
      <g transform="translate(720, 126)" font-family="{MONO}">
        <text x="0" y="0" font-size="9" fill="#C77B9B">CONTRIBUTIONS</text>
        <text x="0" y="20" font-family="{SERIF}" font-size="20" font-weight="700" fill="#F8F0F3">{live_data["total"]:,}</text>
        <text x="118" y="0" font-size="9" fill="#C77B9B">ACTIVE DAYS</text>
        <text x="118" y="20" font-family="{SERIF}" font-size="20" font-weight="700" fill="#F8F0F3">{live_data["active_days"]}</text>
        <text x="220" y="0" font-size="9" fill="#C77B9B">LONGEST STREAK</text>
        <text x="220" y="20" font-family="{SERIF}" font-size="20" font-weight="700" fill="#F8F0F3">{live_data["longest_streak"]}d</text>
        <text x="340" y="0" font-size="9" fill="#C77B9B">BEST DAY</text>
        <text x="340" y="20" font-family="{SERIF}" font-size="20" font-weight="700" fill="#F8F0F3">{live_data["best_day"]}</text>
      </g>'''
        grid = live_data["grid"]
        for col_idx, col_levels in enumerate(grid[:52]):
            for row_idx, lvl in enumerate(col_levels[:7]):
                x = col_idx * 20.6
                y = row_idx * 14.5
                stroke_attr = ' stroke="#451126" stroke-width="0.6"' if lvl == 0 else ""
                cells.append(f'        <rect x="{x:.1f}" y="{y:.1f}" width="14.5" height="10.2" rx="2.5" fill="{PALETTE[lvl]}"{stroke_attr} />')
        grid_y = 158
    else:
        right_label = "AUTO-SYNCS DAILY VIA GITHUB ACTIONS"
        sub_label = "BUILD CADENCE · DECORATIVE PREVIEW (RUN ACTION FOR LIVE DATA)"
        footer_note = f"Run the 'Update Burgundy Profile' GitHub Action to populate live commit counts for @{username}"
        metrics_xml = ""
        for col in range(52):
            for row in range(7):
                val = math.sin(col * 0.28 + row * 0.50) + math.cos(col * 0.13 - row * 0.36)
                lvl = 0 if val < -0.55 else (1 if val < 0.05 else (2 if val < 0.65 else (3 if val < 1.25 else 4)))
                x = col * 20.6
                y = row * 14.5
                stroke_attr = ' stroke="#451126" stroke-width="0.6"' if lvl == 0 else ""
                cells.append(f'        <rect x="{x:.1f}" y="{y:.1f}" width="14.5" height="10.2" rx="2.5" fill="{PALETTE[lvl]}"{stroke_attr} />')
        grid_y = 152

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 315" width="1200" height="315" role="img" aria-labelledby="ym-s5-title ym-s5-desc">
  <title id="ym-s5-title">05 Commit Log — A year of building.</title>
  <desc id="ym-s5-desc">Burgundy GitHub contribution calendar for @{esc(username)}.</desc>
  <defs>
    <linearGradient id="ym-s5-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10070C" />
      <stop offset="55%" stop-color="#190B12" />
      <stop offset="100%" stop-color="#360D1E" />
    </linearGradient>
    <linearGradient id="ym-s5-inner" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#220915" />
      <stop offset="100%" stop-color="#3B0E22" />
    </linearGradient>
    <linearGradient id="ym-s5-sweep" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#701A3D" stop-opacity="0" />
      <stop offset="50%" stop-color="#F8F0F3" stop-opacity="0.22" />
      <stop offset="100%" stop-color="#701A3D" stop-opacity="0" />
    </linearGradient>
    <linearGradient id="ym-s5-line" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#C77B9B" stop-opacity="0.9" />
      <stop offset="50%" stop-color="#701A3D" stop-opacity="0.5" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0.1" />
    </linearGradient>
    <clipPath id="ym-s5-clip"><rect x="1" y="1" width="1198" height="313" rx="16" /></clipPath>
    <clipPath id="ym-s5-gridclip"><rect x="42" y="108" width="1116" height="184" rx="12" /></clipPath>
  </defs>

  <g clip-path="url(#ym-s5-clip)">
    <rect width="1200" height="315" fill="url(#ym-s5-bg)" />

    <g transform="translate(42, 42)">
      <text x="0" y="0" font-family="{MONO}" font-size="11" font-weight="700" fill="#C77B9B" letter-spacing="2">05  COMMIT LOG</text>
      <text x="0" y="34" font-family="{SERIF}" font-size="30" font-weight="700" fill="#F8F0F3">A year of building.</text>
      <text x="1116" y="28" text-anchor="end" font-family="{MONO}" font-size="11" fill="#C77B9B" letter-spacing="1.4">{esc(right_label)}</text>
      <rect x="0" y="48" width="1116" height="1.5" fill="url(#ym-s5-line)" />
    </g>

    <g clip-path="url(#ym-s5-gridclip)">
      <rect x="42" y="108" width="1116" height="184" rx="12" fill="url(#ym-s5-inner)" stroke="#701A3D" stroke-width="1.1" />
      <text x="64" y="136" font-family="{MONO}" font-size="10.5" fill="#E5B5C7" letter-spacing="1.4">{esc(sub_label)}</text>
{metrics_xml}
      <g transform="translate(64, {grid_y})">
{chr(10).join(cells)}
      </g>

      <rect x="-240" y="{grid_y - 4}" width="240" height="110" fill="url(#ym-s5-sweep)">
        <animate attributeName="x" from="-240" to="1220" dur="8s" repeatCount="indefinite" />
      </rect>

      <text x="64" y="278" font-family="{MONO}" font-size="10" fill="#C77B9B">{esc(footer_note)}</text>
    </g>

    <rect x="1" y="1" width="1198" height="313" rx="16" fill="none" stroke="#701A3D" stroke-opacity="0.75" stroke-width="1.3" />
  </g>
</svg>'''


def build_certs_svg(cfg):
    certs = cfg["certifications"][:5]
    n = max(1, len(certs))
    gap = 14
    card_w = (1116 - gap * (n - 1)) / n
    cards_xml = []
    for i, c in enumerate(certs):
        x = i * (card_w + gap)
        stroke = '#C77B9B" stroke-opacity="0.5' if c.get("highlight") else '#701A3D'
        cat_col = "#E5B5C7" if c.get("highlight") else "#C77B9B"
        cards_xml.append(
            f'''      <rect x="{x:.1f}" y="0" width="{card_w:.1f}" height="126" rx="12" fill="url(#ym-s6-card)" stroke="{stroke}" stroke-width="1.1" />
      <text x="{x+16:.1f}" y="24" font-family="{MONO}" font-size="9.5" fill="{cat_col}" letter-spacing="1.4">{esc(c["category"])}</text>
      <text x="{x+16:.1f}" y="52" font-family="{SERIF}" font-size="16" font-weight="700" fill="#F8F0F3">{esc(c["title"])}</text>
      <text x="{x+16:.1f}" y="76" font-family="{SANS}" font-size="11.5" fill="#E5B5C7">{esc(c["line1"])}</text>
      <text x="{x+16:.1f}" y="94" font-family="{SANS}" font-size="11.5" fill="#E5B5C7">{esc(c["line2"])}</text>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 264" width="1200" height="264" role="img" aria-labelledby="ym-s6-title ym-s6-desc">
  <title id="ym-s6-title">06 Certifications &amp; Training — Verified Credentials</title>
  <desc id="ym-s6-desc">Verified certifications and training cards auto-generated from profile.json.</desc>
  <defs>
    <linearGradient id="ym-s6-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10070C" />
      <stop offset="55%" stop-color="#190B12" />
      <stop offset="100%" stop-color="#360D1E" />
    </linearGradient>
    <linearGradient id="ym-s6-card" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#220915" />
      <stop offset="100%" stop-color="#3A0F22" />
    </linearGradient>
    <linearGradient id="ym-s6-line" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#C77B9B" stop-opacity="0.9" />
      <stop offset="50%" stop-color="#701A3D" stop-opacity="0.5" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0.1" />
    </linearGradient>
    <clipPath id="ym-s6-clip"><rect x="1" y="1" width="1198" height="262" rx="16" /></clipPath>
  </defs>

  <g clip-path="url(#ym-s6-clip)">
    <rect width="1200" height="264" fill="url(#ym-s6-bg)" />

    <g transform="translate(42, 42)">
      <text x="0" y="0" font-family="{MONO}" font-size="11" font-weight="700" fill="#C77B9B" letter-spacing="2">06  CERTIFICATIONS &amp; TRAINING</text>
      <text x="0" y="34" font-family="{SERIF}" font-size="30" font-weight="700" fill="#F8F0F3">Verified credentials.</text>
      <text x="1116" y="28" text-anchor="end" font-family="{MONO}" font-size="11" fill="#C77B9B" letter-spacing="1.4">SPECIALIZATIONS · WORKSHOPS · HACKATHON</text>
      <rect x="0" y="48" width="1116" height="1.5" fill="url(#ym-s6-line)" />
    </g>

    <g transform="translate(42, 110)">
{chr(10).join(cards_xml)}
    </g>

    <rect x="1" y="1" width="1198" height="262" rx="16" fill="none" stroke="#701A3D" stroke-opacity="0.75" stroke-width="1.3" />
  </g>
</svg>'''


def build_footer_svg(cfg):
    ident = cfg["identity"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 190" width="1200" height="190" role="img" aria-labelledby="ym-s8-title ym-s8-desc">
  <title id="ym-s8-title">{esc(ident["name"])} — Signature Footer</title>
  <desc id="ym-s8-desc">Cinematic burgundy closing signature banner for {esc(ident["name"])}.</desc>
  <defs>
    <linearGradient id="ym-s8-bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#10070C" />
      <stop offset="50%" stop-color="#290B18">
        <animate attributeName="stop-color" values="#290B18;#3F1024;#290B18" dur="12s" repeatCount="indefinite" />
      </stop>
      <stop offset="100%" stop-color="#10070C" />
    </linearGradient>
    <radialGradient id="ym-s8-glow" cx="50%" cy="48%" r="48%">
      <stop offset="0%" stop-color="#701A3D" stop-opacity="0.55" />
      <stop offset="65%" stop-color="#451126" stop-opacity="0.18" />
      <stop offset="100%" stop-color="#10070C" stop-opacity="0" />
    </radialGradient>
    <linearGradient id="ym-s8-line" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#451126" stop-opacity="0" />
      <stop offset="35%" stop-color="#C77B9B" stop-opacity="0.9" />
      <stop offset="50%" stop-color="#F8F0F3" stop-opacity="1" />
      <stop offset="65%" stop-color="#C77B9B" stop-opacity="0.9" />
      <stop offset="100%" stop-color="#451126" stop-opacity="0" />
    </linearGradient>
    <filter id="ym-s8-blur" x="-20%" y="-40%" width="140%" height="180%">
      <feGaussianBlur stdDeviation="3.5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>
    <clipPath id="ym-s8-clip"><rect x="1" y="1" width="1198" height="188" rx="16" /></clipPath>
  </defs>

  <g clip-path="url(#ym-s8-clip)">
    <rect width="1200" height="190" fill="url(#ym-s8-bg)" />
    <rect width="1200" height="190" fill="url(#ym-s8-glow)" />

    <circle cx="240" cy="64" r="2" fill="#E5B5C7" fill-opacity="0.55">
      <animate attributeName="opacity" values="0.2;0.85;0.2" dur="4s" repeatCount="indefinite" />
    </circle>
    <circle cx="960" cy="58" r="2" fill="#E5B5C7" fill-opacity="0.55">
      <animate attributeName="opacity" values="0.8;0.2;0.8" dur="4.6s" repeatCount="indefinite" />
    </circle>
    <circle cx="320" cy="132" r="1.5" fill="#C77B9B" fill-opacity="0.5" />
    <circle cx="880" cy="126" r="1.5" fill="#C77B9B" fill-opacity="0.5" />

    <text x="600" y="84" text-anchor="middle" font-family="{SERIF}" font-size="44" font-weight="700" fill="#F8F0F3" letter-spacing="1.2">
      {esc(ident["name"])}
    </text>

    <line x1="220" y1="106" x2="980" y2="106" stroke="#451126" stroke-width="1" />
    <line x1="220" y1="106" x2="980" y2="106" stroke="url(#ym-s8-line)" stroke-width="2" stroke-dasharray="220 540" stroke-dashoffset="0" filter="url(#ym-s8-blur)">
      <animate attributeName="stroke-dashoffset" from="760" to="0" dur="6.5s" repeatCount="indefinite" />
    </line>

    <text x="600" y="136" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="16" fill="#E5B5C7">
      {esc(ident["tagline"])}
    </text>
    <text x="600" y="162" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="#C77B9B" letter-spacing="2">
      {esc(ident["role_line"].upper())}
    </text>

    <rect x="1" y="1" width="1198" height="188" rx="16" fill="none" stroke="#701A3D" stroke-opacity="0.75" stroke-width="1.3" />
  </g>
</svg>'''


def build_readme(cfg):
    ident = cfg["identity"]
    email_enc = badge_part(ident["email"].upper())
    user_enc = badge_part(ident["username"].upper())

    proj_blocks = []
    for proj in cfg["projects"]:
        svg_path = f'assets/{proj["id"]}.svg'
        first_url = next((l["url"] for l in proj.get("links", []) if l.get("url")), "")
        if first_url:
            card_html = f'''<div align="center">
  <a href="{first_url}">
    <img src="{svg_path}" alt="{esc(proj["title"])}" width="100%" />
  </a>
</div>'''
        else:
            card_html = f'''<div align="center">
  <img src="{svg_path}" alt="{esc(proj["title"])}" width="100%" />
</div>'''

        badge_lines = []
        for l in proj.get("links", []):
            lbl = badge_part(l["label"])
            txt = badge_part(l["text"])
            if l.get("url"):
                badge_lines.append(
                    f'  <a href="{l["url"]}"><img src="https://img.shields.io/badge/{lbl}-{txt}-701A3D?style=for-the-badge&labelColor=190B12&logo=github&logoColor=E5B5C7" alt="{esc(l["text"])}" /></a>'
                )
            else:
                badge_lines.append(
                    f'  <img src="https://img.shields.io/badge/{lbl}-{txt}-451126?style=for-the-badge&labelColor=190B12&logo=python&logoColor=E5B5C7" alt="{esc(l["text"])}" />'
                )
        badges_html = '<p align="center">\n' + "\n".join(badge_lines) + "\n</p>"
        proj_blocks.append(card_html + "\n" + badges_html)

    return f'''<!-- Auto-generated from profile.json by scripts/generate_profile.py — edit profile.json to update! -->
<div align="center">
  <img src="assets/profile-hero.svg?v=3" alt="{esc(ident["name"])} — {esc(ident["role_line"])}" width="100%" />
</div>

<p align="center">
  <a href="{ident["github"]}"><img src="https://img.shields.io/badge/GITHUB-{user_enc}-701A3D?style=for-the-badge&labelColor=190B12&logo=github&logoColor=E5B5C7" alt="GitHub" /></a>
  <a href="{ident["linkedin"]}"><img src="https://img.shields.io/badge/LINKEDIN-YASHWINI--M-701A3D?style=for-the-badge&labelColor=190B12&logo=linkedin&logoColor=E5B5C7" alt="LinkedIn" /></a>
  <a href="{ident["github"]}?tab=repositories"><img src="https://img.shields.io/badge/REPOSITORIES-EXPLORE-701A3D?style=for-the-badge&labelColor=190B12&logo=git&logoColor=E5B5C7" alt="Repositories" /></a>
  <a href="mailto:{ident["email"]}"><img src="https://img.shields.io/badge/EMAIL-{email_enc}-701A3D?style=for-the-badge&labelColor=190B12&logo=gmail&logoColor=E5B5C7" alt="Email" /></a>
</p>

<div align="center">
  <img src="assets/sec-01-about.svg" alt="01 About — Hello, I'm {esc(ident["first_name"])}." width="100%" />
</div>

<br />

<div align="center">
  <img src="assets/sec-02-experience.svg" alt="02 Experience &amp; Recognition" width="100%" />
</div>

<br />

<div align="center">
  <img src="assets/sec-03-projects-header.svg" alt="03 Selected Work" width="100%" />
</div>

{chr(10).join(proj_blocks)}

<br />

<div align="center">
  <img src="assets/sec-04-skills.svg" alt="04 Technical Stack" width="100%" />
</div>

<br />

<div align="center">
  <a href="{ident["github"]}">
    <img src="assets/sec-05-activity.svg" alt="05 Commit Log — Live GitHub Activity" width="100%" />
  </a>
</div>

<br />

<div align="center">
  <img src="assets/sec-06-certifications.svg" alt="06 Certifications &amp; Training" width="100%" />
</div>

<br />

<div align="center">
  <img src="assets/sec-07-connect-header.svg" alt="07 Connect" width="100%" />
</div>

<p align="center">
  <a href="mailto:{ident["email"]}"><img src="https://img.shields.io/badge/EMAIL-{email_enc}-701A3D?style=for-the-badge&labelColor=190B12&logo=gmail&logoColor=E5B5C7" alt="Email" /></a>
  <a href="{ident["linkedin"]}"><img src="https://img.shields.io/badge/LINKEDIN-YASHWINI--M-701A3D?style=for-the-badge&labelColor=190B12&logo=linkedin&logoColor=E5B5C7" alt="LinkedIn" /></a>
  <a href="{ident["github"]}"><img src="https://img.shields.io/badge/GITHUB-{user_enc}-701A3D?style=for-the-badge&labelColor=190B12&logo=github&logoColor=E5B5C7" alt="GitHub" /></a>
</p>

<div align="center">
  <img src="assets/sec-08-footer.svg" alt="{esc(ident["name"])} — {esc(ident["tagline"])}" width="100%" />
</div>
'''


def main():
    with open("profile.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    write_file("assets/sec-01-about.svg", build_about_svg(cfg))
    write_file("assets/sec-02-experience.svg", build_experience_svg(cfg))
    write_file(
        "assets/sec-03-projects-header.svg",
        build_section_header("ym-s3h", "03  SELECTED WORK", "Systems, built end to end.", "DEEP LEARNING · GENAI · FULL-STACK"),
    )
    for idx, proj in enumerate(cfg["projects"], start=1):
        write_file(f'assets/{proj["id"]}.svg', build_project_card(idx, proj))

    write_file("assets/sec-04-skills.svg", build_skills_svg(cfg))

    live_data = fetch_live_contributions(cfg["identity"]["username"])
    write_file("assets/sec-05-activity.svg", build_activity_svg(cfg, live_data))

    write_file("assets/sec-06-certifications.svg", build_certs_svg(cfg))
    write_file(
        "assets/sec-07-connect-header.svg",
        build_section_header("ym-s7", "07  CONNECT", "Let's build something worth explaining.", "OPEN TO COLLABORATION"),
    )
    write_file("assets/sec-08-footer.svg", build_footer_svg(cfg))
    write_file("README.md", build_readme(cfg))
    print("Profile SVGs and README.md generated successfully from profile.json.")


if __name__ == "__main__":
    main()
