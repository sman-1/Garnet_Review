from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from jinja2 import DictLoader
from better_profanity import profanity
from datetime import datetime
import os

profanity.load_censor_words()

_BANNED_WORDS_PATH = os.path.join(os.path.dirname(__file__), 'banned_words.txt')
if os.path.exists(_BANNED_WORDS_PATH):
    with open(_BANNED_WORDS_PATH) as _f:
        _custom_words = [w.strip() for w in _f if w.strip()]
    profanity.add_censor_words(_custom_words)


def _contains_banned_phrase(text):
    import re
    lowered = text.lower()
    with open(_BANNED_WORDS_PATH) as f:
        for phrase in f:
            phrase = phrase.strip()
            if not phrase:
                continue
            if ' ' in phrase:
                if phrase in lowered:
                    return True
            else:
                if re.search(r'\b' + re.escape(phrase) + r'\b', lowered):
                    return True
    return False


def moderate_review(course_name, author, title, review_text, advice):
    combined = ' '.join(filter(None, [author, title, review_text, advice]))
    if profanity.contains_profanity(combined) or _contains_banned_phrase(combined):
        return False, 'Your review contains inappropriate language. Please keep it respectful.'
    return True, None

# ─── Templates ────────────────────────────────────────────────────────────────

BASE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Garnet Network{% endblock %}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,700&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      theme: {
        extend: {
          colors: {
            'rye-red': '#b61722',
            'rye-red-hover': '#da3437',
            'surface': '#f8f9ff',
            'on-surface': '#121c2a',
          },
          fontFamily: {
            sans: ['"Plus Jakarta Sans"', 'system-ui', 'sans-serif'],
          },
          boxShadow: {
            'hard':    '4px 4px 0px 0px #121c2a',
            'hard-lg': '6px 6px 0px 0px #121c2a',
            'hard-sm': '2px 2px 0px 0px #121c2a',
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: "Plus Jakarta Sans", system-ui, sans-serif; }
    .card-hard { background:#fff; border:2px solid #121c2a; border-radius:8px; box-shadow:4px 4px 0 #121c2a; }
    .card-hard-interactive { background:#fff; border:2px solid #121c2a; border-radius:8px; box-shadow:4px 4px 0 #121c2a; transition:all .2s; }
    .card-hard-interactive:hover { transform:translate(-2px,-2px); box-shadow:6px 6px 0 #121c2a; }
    .card-hard-interactive:active { transform:translate(0,0); box-shadow:none; }
    .btn-hard { border:2px solid #121c2a; box-shadow:4px 4px 0 #121c2a; transition:all .15s; }
    .btn-hard:hover { transform:translate(-1px,-1px); box-shadow:5px 5px 0 #121c2a; }
    .btn-hard:active { transform:translate(2px,2px); box-shadow:none; }
    .star-pick { color:#e5e7eb; cursor:pointer; font-size:2rem; transition:color .1s; user-select:none; }
    .star-pick.active { color:#f59e0b; }
  </style>
</head>
<body class="bg-surface text-on-surface antialiased min-h-screen flex">

  <!-- Sidebar (desktop) -->
  <aside class="fixed left-0 top-0 hidden h-full w-64 flex-col border-r-2 border-on-surface bg-white p-6 md:flex z-40">
    <div class="mb-8 flex items-center gap-3">
      <div class="h-10 w-10 overflow-hidden rounded-full border-2 border-on-surface bg-rye-red flex items-center justify-center">
        <span class="text-white font-black text-sm">RHS</span>
      </div>
      <div>
        <h3 class="font-black leading-none text-sm">Rye Student</h3>
        <p class="text-xs text-on-surface/60 mt-0.5">Garnet Network</p>
      </div>
    </div>

    <a href="#" onclick="event.preventDefault(); document.getElementById('write-review-modal').classList.remove('hidden')"
       class="mb-8 flex w-full items-center justify-center gap-2 rounded-lg border-2 border-on-surface bg-rye-red py-3 font-black text-white btn-hard text-sm">
      <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>
      Write a Review
    </a>

    <nav class="flex flex-1 flex-col gap-1">
      <a href="{{ url_for('index') }}"
         class="flex items-center gap-3 rounded-lg px-3 py-2.5 font-bold text-sm transition-all
                {% if request.endpoint == 'index' %}bg-rye-red text-white{% else %}text-on-surface/60 hover:bg-surface hover:text-on-surface{% endif %}">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
        Home Feed
        {% if request.endpoint == 'index' %}<svg class="ml-auto" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M9 18l6-6-6-6"/></svg>{% endif %}
      </a>
      <a href="{{ url_for('directory') }}"
         class="flex items-center gap-3 rounded-lg px-3 py-2.5 font-bold text-sm transition-all
                {% if request.endpoint == 'directory' %}bg-rye-red text-white{% else %}text-on-surface/60 hover:bg-surface hover:text-on-surface{% endif %}">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
        Course Directory
        {% if request.endpoint == 'directory' %}<svg class="ml-auto" width="14" height="14" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M9 18l6-6-6-6"/></svg>{% endif %}
      </a>
      <a href="{{ url_for('add_course') }}"
         class="flex items-center gap-3 rounded-lg px-3 py-2.5 font-bold text-sm transition-all text-on-surface/60 hover:bg-surface hover:text-on-surface">
        <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v8M8 12h8"/></svg>
        Add a Class
      </a>
    </nav>
  </aside>

  <!-- Main -->
  <div class="flex-1 md:ml-64 flex flex-col min-h-screen">
    <!-- Top header -->
    <header class="sticky top-0 z-30 flex h-16 items-center justify-between border-b-2 border-on-surface bg-white px-4 md:px-8">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-black text-rye-red md:text-2xl tracking-tight">Garnet Network</h1>
      </div>
      <div class="flex items-center gap-3">
        <form method="GET" action="{{ url_for('directory') }}" class="relative hidden sm:block">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface/40" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
          <input type="text" name="search" placeholder="Search courses…"
                 class="w-56 rounded-lg border border-on-surface/20 bg-surface py-2 pl-9 pr-4 text-sm focus:border-on-surface focus:outline-none font-medium">
        </form>
        <a href="#" onclick="event.preventDefault(); document.getElementById('write-review-modal').classList.remove('hidden')"
           class="md:hidden rounded-lg border-2 border-on-surface bg-rye-red px-3 py-1.5 text-xs font-black text-white btn-hard">
          + Review
        </a>
      </div>
    </header>

    <main class="flex-1 p-4 md:p-8">
      {% block content %}{% endblock %}
    </main>
  </div>

  <!-- Quick write-review modal -->
  <div id="write-review-modal" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-on-surface/60 p-4">
    <div class="card-hard w-full max-w-md p-8">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl font-black">Choose a Course to Review</h2>
        <button onclick="document.getElementById('write-review-modal').classList.add('hidden')"
                class="text-on-surface/40 hover:text-on-surface transition-colors text-2xl leading-none">&times;</button>
      </div>
      <div class="mb-4">
        <label class="block text-xs font-black uppercase mb-2 tracking-wider">Course</label>
        <select id="modal-course-select" class="w-full rounded border-2 border-on-surface/20 bg-surface py-2 px-3 text-sm font-medium focus:border-on-surface outline-none">
          <option value="">Select a course…</option>
          {% for c in all_courses_for_modal %}
          <option value="{{ url_for('add_review', course_id=c.id) }}">{{ c.name }} {% if c.department %}({{ c.department }}){% endif %}</option>
          {% endfor %}
        </select>
      </div>
      <button type="button" onclick="if(document.getElementById('modal-course-select').value) window.location=document.getElementById('modal-course-select').value"
              class="w-full rounded-lg border-2 border-on-surface bg-rye-red py-3 font-black text-white btn-hard text-sm">
        Continue →
      </button>
    </div>
  </div>

  {% block scripts %}{% endblock %}
</body>
</html>"""

INDEX_HTML = """{% extends "base.html" %}
{% block title %}Home Feed — Garnet Network{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto">

  <!-- Stats bento -->
  <div class="grid grid-cols-1 gap-6 sm:grid-cols-3 mb-12">
    <div class="card-hard p-6">
      <div class="mb-4 flex items-center gap-2">
        <svg class="text-rye-red" width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        <span class="text-xs font-black uppercase tracking-wider">Total Reviews</span>
      </div>
      <div class="text-4xl font-black">{{ total_reviews }}</div>
    </div>
    <div class="bg-rye-red border-2 border-on-surface rounded-lg p-6 shadow-hard text-white">
      <div class="mb-4 flex items-center gap-2">
        <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
        <span class="text-xs font-black uppercase tracking-wider">Courses Listed</span>
      </div>
      <div class="text-4xl font-black">{{ total_courses }}</div>
    </div>
    <div class="bg-on-surface border-2 border-on-surface rounded-lg p-6 shadow-hard text-white">
      <div class="mb-4 flex items-center gap-2">
        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        <span class="text-xs font-black uppercase tracking-wider">Avg Rating</span>
      </div>
      <div class="text-4xl font-black flex items-baseline gap-1">
        {{ avg_rating }}<span class="text-xl font-bold opacity-40">/5</span>
      </div>
    </div>
  </div>

  <div class="grid grid-cols-1 gap-8 lg:grid-cols-12">

    <!-- Activity feed -->
    <div class="lg:col-span-8">
      <div class="mb-6 flex items-end justify-between border-b-2 border-on-surface pb-2">
        <h2 class="text-2xl font-black">Recent Reviews</h2>
        <a href="{{ url_for('directory') }}" class="text-sm font-black text-on-surface/40 hover:text-rye-red transition-colors">Browse all →</a>
      </div>

      {% if recent_reviews %}
      <div class="flex flex-col gap-6">
        {% for review in recent_reviews %}
        <article class="card-hard-interactive overflow-hidden">
          <div class="border-b-2 border-on-surface bg-surface px-6 py-3 flex justify-between items-center">
            <div>
              <a href="{{ url_for('course_detail', course_id=review.course_id) }}" class="font-black hover:text-rye-red transition-colors">{{ review.course.name }}</a>
              <p class="text-xs text-on-surface/60 mt-0.5">{{ review.course.department }}{% if review.semester %} &bull; {{ review.semester }}{% endif %}</p>
            </div>
            <span class="rounded border border-on-surface bg-white px-2 py-0.5 text-[10px] font-black uppercase whitespace-nowrap">
              {{ review.course.course_type }}
            </span>
          </div>
          <div class="p-6 relative">
            <div class="absolute right-6 top-6 h-12 w-12 bg-rye-red text-white border-2 border-on-surface rounded-full flex items-center justify-center font-black text-lg">
              {{ review.overall }}.0
            </div>
            <div class="mb-3 flex items-center gap-2">
              <div class="h-8 w-8 rounded-full bg-surface border-2 border-on-surface flex items-center justify-center font-black text-xs text-rye-red">
                {{ review.author[:2].upper() }}
              </div>
              <div>
                <p class="text-sm font-black leading-none">{{ review.grade_level or 'Student' }}{% if review.grade_earned %} &bull; Grade: {{ review.grade_earned }}{% endif %}</p>
                <p class="text-[10px] text-on-surface/40 mt-0.5">{{ review.created_at.strftime('%b %d, %Y') }}</p>
              </div>
            </div>
            {% if review.title %}
            <p class="font-black italic mb-2 pr-16 text-base">"{{ review.title }}"</p>
            {% endif %}
            {% if review.review_text %}
            <p class="text-sm leading-relaxed pr-16 text-on-surface/70 line-clamp-3">{{ review.review_text }}</p>
            {% endif %}
          </div>
          <div class="flex items-center gap-6 border-t border-on-surface/10 bg-surface/50 px-6 py-3">
            <button onclick="likeReview({{ review.id }}, this)"
                    class="flex items-center gap-1.5 text-xs font-black text-on-surface/60 hover:text-rye-red transition-colors">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>
              <span class="like-count">{{ review.likes }}</span>
            </button>
            <a href="{{ url_for('course_detail', course_id=review.course_id) }}"
               class="flex items-center gap-1.5 text-xs font-black text-on-surface/60 hover:text-on-surface transition-colors">
              <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
              See Full Review
            </a>
          </div>
        </article>
        {% endfor %}
      </div>
      {% else %}
      <div class="card-hard p-16 text-center">
        <p class="text-4xl mb-4">✍️</p>
        <h3 class="text-xl font-black mb-2">No reviews yet</h3>
        <p class="text-on-surface/60 mb-6">Be the first Garnet to rate a course.</p>
        <a href="{{ url_for('directory') }}" class="inline-block rounded-lg border-2 border-on-surface bg-rye-red px-6 py-2.5 font-black text-white btn-hard text-sm">Browse Courses</a>
      </div>
      {% endif %}
    </div>

    <!-- Right sidebar -->
    <div class="lg:col-span-4 flex flex-col gap-6">
      <div class="card-hard p-6">
        <div class="mb-4 flex items-center gap-2 border-b-2 border-on-surface pb-2">
          <svg class="text-rye-red" width="18" height="18" fill="currentColor" viewBox="0 0 24 24"><path d="M12 12c2.7-2.7 6-4 6-4s-1.3 3.3-4 6-6 4-6 4 1.3-3.3 4-6zM12 12L2 22"/><path d="M20 4v6M20 4h-6"/></svg>
          <h3 class="font-black uppercase tracking-tight text-sm">Trending Courses</h3>
        </div>
        {% if trending %}
        <div class="flex flex-col gap-3">
          {% for course in trending %}
          <a href="{{ url_for('course_detail', course_id=course.id) }}"
             class="flex items-center justify-between rounded-lg border border-on-surface/20 bg-surface p-3 text-left transition-all hover:border-on-surface hover:shadow-hard-sm">
            <div class="flex-1 min-w-0 mr-3">
              <p class="text-sm font-black truncate">{{ course.name }}</p>
              <p class="text-[10px] text-on-surface/40">{{ course.review_count }} review{{ 's' if course.review_count != 1 }}</p>
            </div>
            <div class="text-right flex-shrink-0">
              <span class="text-lg font-black text-rye-red">{{ course.avg_overall }}</span>
              <div class="mt-1 h-1 w-10 overflow-hidden rounded-full bg-on-surface/10">
                <div class="h-full bg-rye-red rounded-full" style="width:{{ (course.avg_overall / 5 * 100)|int }}%"></div>
              </div>
            </div>
          </a>
          {% endfor %}
        </div>
        {% else %}
        <p class="text-sm text-on-surface/40">Reviews coming soon.</p>
        {% endif %}
        <a href="{{ url_for('directory', sort='reviews') }}"
           class="mt-5 flex w-full items-center justify-center gap-2 rounded-lg border-2 border-on-surface bg-white py-2 text-xs font-black transition-all hover:bg-surface btn-hard">
          View All Courses
        </a>
      </div>

      <div class="card-hard bg-rye-red p-6 text-white overflow-hidden relative">
        <div class="relative z-10">
          <h3 class="text-xl font-black mb-2">Help your fellow Garnets.</h3>
          <p class="text-sm mb-5 opacity-90">Rate a class you've taken and give future students the real scoop.</p>
          <a href="{{ url_for('directory') }}"
             class="inline-block rounded-lg bg-white px-5 py-2 text-sm font-black text-rye-red transition-all hover:-translate-y-0.5 shadow-hard-sm">
            Pick a Course →
          </a>
        </div>
        <div class="absolute -bottom-8 -right-8 h-36 w-36 rounded-full bg-white opacity-10 blur-2xl pointer-events-none"></div>
      </div>
    </div>
  </div>
</div>

<script>
function likeReview(id, btn) {
  fetch('/review/' + id + '/like', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      btn.querySelector('.like-count').textContent = data.likes;
      btn.classList.add('text-rye-red');
      btn.disabled = true;
    });
}
</script>
{% endblock %}"""

DIRECTORY_HTML = """{% extends "base.html" %}
{% block title %}Course Directory — Garnet Network{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto">

  <header class="mb-10">
    <h1 class="text-4xl font-black mb-2 tracking-tighter">Course Directory</h1>
    <p class="text-lg text-on-surface/60 max-w-2xl font-medium">
      Browse every class in the official 2024–25 RHS catalog. Filter by department, sort by difficulty, or search by name.
    </p>
  </header>

  <form method="GET" action="{{ url_for('directory') }}">
    <div class="card-hard p-6 mb-10 bg-surface">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
        <div class="md:col-span-1">
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Find a Course</label>
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 text-on-surface/40" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
            <input type="text" name="search" value="{{ search }}"
                   placeholder="e.g. AP Calculus, English 11…"
                   class="w-full rounded border border-on-surface/20 bg-white py-2 pl-9 pr-4 text-sm focus:border-on-surface focus:outline-none font-medium">
          </div>
        </div>
        <div>
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Department</label>
          <select name="dept" class="w-full rounded border border-on-surface/20 bg-white py-2 px-3 text-sm focus:border-on-surface outline-none font-medium">
            <option value="">All Departments</option>
            {% for d in departments %}
            <option value="{{ d }}" {% if dept == d %}selected{% endif %}>{{ d }}</option>
            {% endfor %}
          </select>
        </div>
        <div>
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Type</label>
          <select name="type" class="w-full rounded border border-on-surface/20 bg-white py-2 px-3 text-sm focus:border-on-surface outline-none font-medium">
            <option value="">All Types</option>
            {% for t in course_types %}
            <option value="{{ t }}" {% if course_type == t %}selected{% endif %}>{{ t }}</option>
            {% endfor %}
          </select>
        </div>
        <div>
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Sort By</label>
          <select name="sort" class="w-full rounded border border-on-surface/20 bg-white py-2 px-3 text-sm focus:border-on-surface outline-none font-medium">
            <option value="name"            {% if sort=='name' %}selected{% endif %}>Name (A–Z)</option>
            <option value="rating"          {% if sort=='rating' %}selected{% endif %}>Highest Rated</option>
            <option value="difficulty_high" {% if sort=='difficulty_high' %}selected{% endif %}>Difficulty (High→Low)</option>
            <option value="difficulty_low"  {% if sort=='difficulty_low' %}selected{% endif %}>Difficulty (Low→High)</option>
            <option value="reviews"         {% if sort=='reviews' %}selected{% endif %}>Most Reviewed</option>
          </select>
        </div>
      </div>
      <div class="mt-4 flex items-center justify-between">
        <p class="text-sm text-on-surface/60 font-medium">{{ courses|length }} course{{ 's' if courses|length != 1 }} found</p>
        <div class="flex gap-2">
          <button type="submit" class="rounded-lg border-2 border-on-surface bg-rye-red px-5 py-1.5 text-sm font-black text-white btn-hard">Apply</button>
          <a href="{{ url_for('directory') }}" class="rounded-lg border-2 border-on-surface bg-white px-5 py-1.5 text-sm font-black btn-hard">Clear</a>
        </div>
      </div>
    </div>
  </form>

  {% if courses %}
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for course in courses %}
    <a href="{{ url_for('course_detail', course_id=course.id) }}"
       class="card-hard-interactive flex flex-col group">
      <div class="bg-surface px-5 py-3 border-b-2 border-on-surface flex justify-between items-center rounded-t-lg">
        <span class="text-[10px] font-black uppercase tracking-widest text-on-surface/60">{{ course.code or '—' }}</span>
        <span class="text-[10px] font-black uppercase border border-on-surface/20 px-2 py-0.5 rounded bg-white
          {% if course.course_type == 'AP' %}text-rye-red border-rye-red/30{% elif course.course_type == 'Honors' %}text-on-surface{% else %}text-on-surface/60{% endif %}">
          {{ course.course_type }}
        </span>
      </div>
      <div class="p-5 flex flex-col flex-1">
        <h3 class="text-lg font-black mb-0.5 group-hover:text-rye-red transition-colors leading-tight">{{ course.name }}</h3>
        <p class="text-xs text-on-surface/50 font-bold mb-3">{{ course.department }}{% if course.grades %} &bull; Gr. {{ course.grades }}{% endif %}{% if course.credits %} &bull; {{ course.credits }} cr.{% endif %}</p>
        {% if course.description %}
        <p class="text-sm text-on-surface/70 leading-relaxed line-clamp-3 mb-4 flex-1">{{ course.description }}</p>
        {% else %}
        <div class="flex-1"></div>
        {% endif %}
        <div class="mt-auto pt-4 border-t border-on-surface/10">
          {% if course.review_count > 0 %}
          <div class="flex justify-between items-end">
            <div>
              <p class="text-[10px] font-black uppercase text-on-surface/40 mb-1">Avg Rating</p>
              <div class="flex items-center gap-1">
                {% for i in range(1,6) %}
                <svg width="13" height="13" fill="{{ '#b61722' if i <= course.avg_overall|int else 'none' }}" stroke="#b61722" stroke-width="2.5" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                {% endfor %}
                <span class="text-xs font-black ml-1">{{ course.avg_overall }}</span>
              </div>
            </div>
            <div class="text-right">
              <p class="text-[10px] font-black uppercase text-on-surface/40 mb-1">Difficulty</p>
              {% if course.difficulty_label %}
              <span class="text-[10px] font-black uppercase px-2 py-1 rounded border-2 border-on-surface
                {% if course.difficulty_label == 'Hard' %}bg-rye-red text-white{% elif course.difficulty_label == 'Medium' %}bg-on-surface text-white{% else %}bg-surface{% endif %}">
                {{ course.difficulty_label }}
              </span>
              {% endif %}
            </div>
          </div>
          <p class="text-[10px] text-on-surface/40 font-bold mt-2">{{ course.review_count }} student review{{ 's' if course.review_count != 1 }}</p>
          {% else %}
          <div class="flex items-center justify-between">
            <p class="text-xs text-on-surface/40 italic">No reviews yet</p>
            <span class="text-xs font-black text-rye-red">Be first →</span>
          </div>
          {% endif %}
        </div>
      </div>
    </a>
    {% endfor %}
  </div>

  <div class="mt-10 text-center">
    <a href="{{ url_for('add_course') }}"
       class="inline-flex items-center gap-2 rounded-lg border-2 border-on-surface bg-white px-8 py-3 font-black btn-hard text-sm">
      <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>
      Don't see your class? Add it
    </a>
  </div>

  {% else %}
  <div class="card-hard p-20 text-center">
    <p class="text-4xl mb-4">🔍</p>
    <h3 class="text-xl font-black mb-2">No courses found</h3>
    <p class="text-on-surface/60 mb-6">Try a different search or filter.</p>
    <div class="flex gap-3 justify-center flex-wrap">
      <a href="{{ url_for('directory') }}" class="rounded-lg border-2 border-on-surface bg-white px-5 py-2 font-black btn-hard text-sm">Clear Filters</a>
      <a href="{{ url_for('add_course') }}" class="rounded-lg border-2 border-on-surface bg-rye-red px-5 py-2 font-black text-white btn-hard text-sm">Add a Class</a>
    </div>
  </div>
  {% endif %}

</div>
{% endblock %}"""

COURSE_DETAIL_HTML = """{% extends "base.html" %}
{% block title %}{{ course.name }} — Garnet Network{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto">

  <a href="{{ url_for('directory') }}" class="inline-flex items-center gap-1.5 text-sm font-black text-on-surface/60 hover:text-rye-red transition-colors mb-8">
    <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
    Back to Directory
  </a>

  <!-- Course header -->
  <div class="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6 border-b-4 border-on-surface pb-6">
    <div class="flex-1">
      <div class="flex flex-wrap gap-2 mb-3">
        <span class="rounded-full bg-surface border border-on-surface/20 px-4 py-1 text-[10px] font-black uppercase tracking-widest">{{ course.department }}</span>
        <span class="rounded-full px-4 py-1 text-[10px] font-black uppercase tracking-widest border-2
          {% if course.course_type == 'AP' %}bg-rye-red text-white border-rye-red{% elif course.course_type == 'Honors' %}bg-on-surface text-white border-on-surface{% else %}bg-surface border-on-surface/20{% endif %}">
          {{ course.course_type }}
        </span>
        {% if course.grades %}<span class="rounded-full bg-surface border border-on-surface/20 px-4 py-1 text-[10px] font-black uppercase tracking-widest">Grades {{ course.grades }}</span>{% endif %}
        {% if course.credits %}<span class="rounded-full bg-surface border border-on-surface/20 px-4 py-1 text-[10px] font-black uppercase tracking-widest">{{ course.credits }} Credit{% if course.credits != '½' %}s{% endif %}</span>{% endif %}
      </div>
      <h1 class="text-4xl md:text-5xl font-black tracking-tighter leading-none">{{ course.name }}</h1>
      {% if course.code %}<p class="text-sm text-on-surface/40 font-bold mt-2">Course code: {{ course.code }}</p>{% endif %}
    </div>

    {% if course.review_count > 0 %}
    <div class="card-hard p-5 flex items-center gap-6 flex-shrink-0">
      <div class="pr-5 border-r-2 border-on-surface/10 text-center">
        <div class="flex items-center gap-1 text-rye-red justify-center">
          <span class="text-4xl font-black">{{ course.avg_overall }}</span>
          <svg width="22" height="22" fill="currentColor" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
        </div>
        <span class="text-[10px] font-black uppercase text-on-surface/40">Overall</span>
      </div>
      <div class="flex flex-col gap-2 min-w-[120px]">
        {% for label, val in [('Difficulty', course.avg_difficulty), ('Teacher', course.avg_teacher), ('Workload', course.avg_workload)] %}
        <div class="flex items-center gap-2">
          <span class="text-[10px] font-black uppercase text-on-surface/40 w-16">{{ label }}</span>
          <div class="h-1.5 flex-1 rounded-full bg-on-surface/10 overflow-hidden">
            <div class="h-full bg-rye-red rounded-full" style="width:{{ (val/5*100)|int }}%"></div>
          </div>
          <span class="text-xs font-black w-5">{{ val }}</span>
        </div>
        {% endfor %}
      </div>
    </div>
    {% endif %}
  </div>

  <div class="grid grid-cols-1 md:grid-cols-12 gap-8">
    <div class="md:col-span-8 flex flex-col gap-8">

      {% if course.description %}
      <section class="card-hard p-8">
        <h2 class="text-xl font-black mb-3 border-b-2 border-on-surface pb-2">About This Course</h2>
        <p class="text-base text-on-surface/70 leading-loose">{{ course.description }}</p>
      </section>
      {% endif %}

      <section>
        <div class="mb-5 flex items-center justify-between border-b-2 border-on-surface pb-2">
          <h2 class="text-xl font-black">Student Reviews
            {% if reviews %}<span class="text-on-surface/40 font-normal text-base">({{ reviews|length }})</span>{% endif %}
          </h2>
          <a href="{{ url_for('add_review', course_id=course.id) }}"
             class="flex items-center gap-1.5 rounded-lg border-2 border-on-surface bg-rye-red px-4 py-2 text-sm font-black text-white btn-hard">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>
            Write a Review
          </a>
        </div>

        {% if reviews %}
        <div class="flex flex-col gap-6">
          {% for review in reviews %}
          <div class="card-hard p-6">
            <div class="flex items-start justify-between mb-4 gap-4">
              <div class="flex items-center gap-3">
                <div class="h-10 w-10 rounded-full bg-rye-red/10 border-2 border-on-surface flex items-center justify-center font-black text-sm text-rye-red flex-shrink-0">
                  {{ review.author[:2].upper() }}
                </div>
                <div>
                  <p class="font-black leading-none text-sm">{{ review.author }}</p>
                  <p class="text-[10px] text-on-surface/40 mt-0.5">
                    {{ review.grade_level or '' }}
                    {% if review.grade_earned %} &bull; Earned: {{ review.grade_earned }}{% endif %}
                    {% if review.semester %} &bull; {{ review.semester }}{% endif %}
                  </p>
                </div>
              </div>
              <div class="flex flex-col items-end gap-1 flex-shrink-0">
                <div class="flex text-rye-red">
                  {% for i in range(1,6) %}
                  <svg width="14" height="14" fill="{{ '#b61722' if i <= review.overall else 'none' }}" stroke="#b61722" stroke-width="2.5" viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
                  {% endfor %}
                </div>
                <span class="text-[10px] text-on-surface/40 font-bold">{{ review.created_at.strftime('%b %d, %Y') }}</span>
              </div>
            </div>

            <div class="flex flex-wrap gap-2 mb-4">
              <span class="text-[10px] font-black uppercase px-2 py-1 rounded-full bg-orange-50 border border-orange-200 text-orange-700">Difficulty: {{ review.difficulty }}/5</span>
              <span class="text-[10px] font-black uppercase px-2 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700">Teacher: {{ review.teacher_rating }}/5</span>
              <span class="text-[10px] font-black uppercase px-2 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700">Workload: {{ review.workload }}/5</span>
              {% if review.would_recommend %}
              <span class="text-[10px] font-black uppercase px-2 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700">👍 Recommends</span>
              {% else %}
              <span class="text-[10px] font-black uppercase px-2 py-1 rounded-full bg-red-50 border border-red-200 text-red-700">👎 Not recommended</span>
              {% endif %}
            </div>

            {% if review.title %}
            <h4 class="font-black italic text-base mb-2">"{{ review.title }}"</h4>
            {% endif %}

            {% if review.review_text %}
            <p class="text-sm leading-relaxed text-on-surface/80 mb-3">{{ review.review_text }}</p>
            {% endif %}

            {% if review.advice %}
            <div class="rounded-lg border-l-4 border-amber-400 bg-amber-50 px-4 py-3 mb-3">
              <p class="text-[10px] font-black uppercase tracking-wider text-amber-700 mb-1">💡 Advice for Future Students</p>
              <p class="text-sm leading-relaxed text-on-surface/80">{{ review.advice }}</p>
            </div>
            {% endif %}

            {% if review.materials %}
            <div class="rounded-lg border-l-4 border-blue-400 bg-blue-50 px-4 py-3 mb-3">
              <p class="text-[10px] font-black uppercase tracking-wider text-blue-700 mb-1">📚 Materials Needed</p>
              <p class="text-sm leading-relaxed text-on-surface/80">{{ review.materials }}</p>
            </div>
            {% endif %}

            <div class="flex items-center justify-between pt-3 border-t border-on-surface/10 mt-2">
              <button onclick="likeReview({{ review.id }}, this)"
                      class="flex items-center gap-1.5 text-xs font-black text-on-surface/50 hover:text-rye-red transition-colors">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg>
                <span class="like-count">{{ review.likes }}</span> Helpful
              </button>
              <form method="POST" action="{{ url_for('delete_review', review_id=review.id) }}"
                    onsubmit="return confirm('Remove this review?')">
                <button type="submit" class="text-[10px] font-black text-on-surface/30 hover:text-red-500 transition-colors uppercase">Remove</button>
              </form>
            </div>
          </div>
          {% endfor %}
        </div>
        {% else %}
        <div class="card-hard p-14 text-center">
          <p class="text-3xl mb-4">✍️</p>
          <h3 class="text-lg font-black mb-2">No reviews yet</h3>
          <p class="text-on-surface/60 text-sm mb-5">Be the first Garnet to rate this course.</p>
          <a href="{{ url_for('add_review', course_id=course.id) }}"
             class="inline-block rounded-lg border-2 border-on-surface bg-rye-red px-6 py-2.5 font-black text-white btn-hard text-sm">
            Write the First Review
          </a>
        </div>
        {% endif %}
      </section>
    </div>

    <!-- Sidebar -->
    <div class="md:col-span-4 flex flex-col gap-5">
      {% if course.review_count > 0 %}
      <div class="card-hard p-5 text-center
        {% if course.recommend_pct >= 70 %}bg-emerald-50{% elif course.recommend_pct >= 40 %}bg-amber-50{% else %}bg-red-50{% endif %}">
        <p class="text-4xl font-black
          {% if course.recommend_pct >= 70 %}text-emerald-600{% elif course.recommend_pct >= 40 %}text-amber-600{% else %}text-red-600{% endif %}">
          {{ course.recommend_pct }}%
        </p>
        <p class="text-xs font-black uppercase tracking-wider text-on-surface/60 mt-1">of students recommend this course</p>
      </div>
      {% endif %}

      <a href="{{ url_for('add_review', course_id=course.id) }}"
         class="flex w-full items-center justify-center gap-2 rounded-lg border-2 border-on-surface bg-rye-red py-3 font-black text-white btn-hard text-sm">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>
        Write a Review
      </a>

      <div class="card-hard p-5">
        <h3 class="text-xs font-black uppercase tracking-widest text-on-surface/40 mb-4 border-b border-on-surface/10 pb-2">Quick Facts</h3>
        <div class="flex flex-col gap-3">
          {% if course.department %}<div class="flex justify-between text-sm"><span class="font-black text-on-surface/50">Department</span><span class="font-bold">{{ course.department }}</span></div>{% endif %}
          {% if course.course_type %}<div class="flex justify-between text-sm"><span class="font-black text-on-surface/50">Type</span><span class="font-bold">{{ course.course_type }}</span></div>{% endif %}
          {% if course.grades %}<div class="flex justify-between text-sm"><span class="font-black text-on-surface/50">Grades</span><span class="font-bold">{{ course.grades }}</span></div>{% endif %}
          {% if course.credits %}<div class="flex justify-between text-sm"><span class="font-black text-on-surface/50">Credits</span><span class="font-bold">{{ course.credits }}</span></div>{% endif %}
          {% if course.code %}<div class="flex justify-between text-sm"><span class="font-black text-on-surface/50">Code</span><span class="font-bold font-mono">{{ course.code }}</span></div>{% endif %}
          {% if course.review_count > 0 %}
          <div class="flex justify-between text-sm"><span class="font-black text-on-surface/50">Reviews</span><span class="font-bold">{{ course.review_count }}</span></div>
          {% endif %}
        </div>
      </div>

      <form method="POST" action="{{ url_for('delete_course', course_id=course.id) }}"
            onsubmit="return confirm('Delete this course and all its reviews?')">
        <button type="submit" class="w-full rounded-lg border-2 border-on-surface/20 bg-white py-2.5 text-xs font-black text-on-surface/40 hover:border-red-400 hover:bg-red-50 hover:text-red-600 transition-all">
          Delete Course
        </button>
      </form>
    </div>
  </div>
</div>

<script>
function likeReview(id, btn) {
  fetch('/review/' + id + '/like', { method: 'POST' })
    .then(r => r.json())
    .then(data => {
      btn.querySelector('.like-count').textContent = data.likes;
      btn.classList.add('text-rye-red');
      btn.disabled = true;
    });
}
</script>
{% endblock %}"""

ADD_REVIEW_HTML = """{% extends "base.html" %}
{% block title %}Review {{ course.name }} — Garnet Network{% endblock %}
{% block content %}
<div class="max-w-3xl mx-auto">

  <header class="mb-10 flex items-center justify-between border-b-2 border-on-surface pb-4">
    <a href="{{ url_for('course_detail', course_id=course.id) }}"
       class="flex items-center gap-2 text-on-surface/60 hover:text-rye-red transition-colors group font-bold text-sm">
      <svg class="group-hover:-translate-x-1 transition-transform" width="18" height="18" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
      Cancel
    </a>
    <span class="text-base font-black text-rye-red">Garnet Network</span>
    <div class="w-16"></div>
  </header>

  {% if error %}
  <div class="mb-6 rounded-lg border-2 border-red-400 bg-red-50 px-5 py-4 flex items-start gap-3">
    <svg class="text-red-500 mt-0.5 flex-shrink-0" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
    <p class="text-sm font-bold text-red-700">{{ error }}</p>
  </div>
  {% endif %}

  <div class="mb-10">
    <h1 class="text-4xl font-black mb-1 tracking-tighter">Rate a Course</h1>
    <p class="text-lg text-on-surface/60 font-medium">Reviewing <strong class="text-on-surface">{{ course.name }}</strong></p>
  </div>

  <form method="POST" id="reviewForm" class="flex flex-col gap-8">

    <!-- Step 1 -->
    <div class="card-hard p-8 relative">
      <div class="absolute -top-4 -left-4 h-10 w-10 bg-rye-red text-white border-2 border-on-surface rounded-full flex items-center justify-center font-black text-xl shadow-hard-sm">1</div>
      <h3 class="text-xl font-black mb-5">About You <span class="text-sm font-normal text-on-surface/40">(optional — all anonymous)</span></h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Nickname</label>
          <input type="text" name="author" placeholder="e.g. Anonymous, GarnetSenior"
                 class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2.5 px-4 text-sm font-medium focus:border-on-surface outline-none transition-all">
        </div>
        <div>
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Grade When Taken</label>
          <select name="grade_level" class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2.5 px-4 text-sm font-medium focus:border-on-surface outline-none">
            <option value="">Select grade</option>
            {% for g in grade_levels %}<option value="{{ g }}">{{ g }}</option>{% endfor %}
          </select>
        </div>
        <div>
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Grade Earned</label>
          <select name="grade_earned" class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2.5 px-4 text-sm font-medium focus:border-on-surface outline-none">
            <option value="">Select grade</option>
            {% for g in grades_earned %}<option value="{{ g }}">{{ g }}</option>{% endfor %}
          </select>
        </div>
        <div>
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Semester</label>
          <select name="semester" class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2.5 px-4 text-sm font-medium focus:border-on-surface outline-none">
            <option value="">Select semester</option>
            {% for s in semesters %}<option value="{{ s }}">{{ s }}</option>{% endfor %}
          </select>
        </div>
      </div>
    </div>

    <!-- Step 2 -->
    <div class="card-hard p-8 relative">
      <div class="absolute -top-4 -left-4 h-10 w-10 bg-rye-red text-white border-2 border-on-surface rounded-full flex items-center justify-center font-black text-xl shadow-hard-sm">2</div>
      <h3 class="text-xl font-black mb-6">Your Ratings</h3>

      <div class="mb-8">
        <p class="text-sm font-black mb-1">Overall Experience <span class="text-rye-red">*</span></p>
        <p class="text-[10px] font-bold uppercase tracking-wider text-on-surface/40 mb-3">How much did you enjoy this class overall?</p>
        <div class="flex items-center gap-1 star-picker" data-name="overall">
          {% for i in range(1,6) %}<span class="star-pick" data-val="{{ i }}">★</span>{% endfor %}
          <input type="hidden" name="overall" id="overall" required>
          <span class="ml-3 text-sm font-black text-on-surface/60" id="overall-desc"></span>
        </div>
      </div>

      <div class="mb-8">
        <div class="flex justify-between items-end mb-3">
          <div>
            <p class="text-sm font-black">Difficulty Level <span class="text-rye-red">*</span></p>
            <p class="text-[10px] font-bold uppercase tracking-wider text-on-surface/40">1 = Easy A &nbsp;·&nbsp; 5 = Very Demanding</p>
          </div>
          <span class="text-2xl font-black text-rye-red" id="difficulty-display">—<span class="text-on-surface/40 text-lg">/5</span></span>
        </div>
        <div class="flex h-14 rounded-lg border-2 border-on-surface overflow-hidden">
          {% for i in range(1,6) %}
          <button type="button" data-val="{{ i }}"
                  class="diff-btn flex-1 font-black text-lg transition-colors bg-white hover:bg-surface border-r-2 border-on-surface last:border-0">{{ i }}</button>
          {% endfor %}
        </div>
        <input type="hidden" name="difficulty" id="difficulty" required>
        <div class="mt-1.5 flex justify-between text-[10px] font-black uppercase text-on-surface/40 tracking-wider">
          <span>Easy A</span><span>Very Demanding</span>
        </div>
      </div>

      <div class="mb-8">
        <p class="text-sm font-black mb-1">Teacher Rating <span class="text-rye-red">*</span></p>
        <p class="text-[10px] font-bold uppercase tracking-wider text-on-surface/40 mb-3">How helpful and effective was the teacher?</p>
        <div class="flex items-center gap-1 star-picker" data-name="teacher_rating">
          {% for i in range(1,6) %}<span class="star-pick" data-val="{{ i }}">★</span>{% endfor %}
          <input type="hidden" name="teacher_rating" id="teacher_rating" required>
          <span class="ml-3 text-sm font-black text-on-surface/60" id="teacher_rating-desc"></span>
        </div>
      </div>

      <div class="mb-8">
        <p class="text-sm font-black mb-1">Workload <span class="text-rye-red">*</span></p>
        <p class="text-[10px] font-bold uppercase tracking-wider text-on-surface/40 mb-3">1 = Very Light &nbsp;·&nbsp; 5 = Very Heavy</p>
        <div class="flex items-center gap-1 star-picker" data-name="workload">
          {% for i in range(1,6) %}<span class="star-pick" data-val="{{ i }}">★</span>{% endfor %}
          <input type="hidden" name="workload" id="workload" required>
          <span class="ml-3 text-sm font-black text-on-surface/60" id="workload-desc"></span>
        </div>
      </div>

      <div>
        <p class="text-sm font-black mb-3">Would You Recommend This Class?</p>
        <div class="flex gap-3 flex-wrap">
          <label class="recommend-option flex-1">
            <input type="radio" name="would_recommend" value="yes" class="sr-only" checked>
            <span class="recommend-btn yes flex items-center justify-center gap-2 rounded-lg border-2 border-on-surface/20 bg-white px-5 py-3 font-black text-sm cursor-pointer transition-all hover:border-on-surface w-full">
              👍 Yes, definitely
            </span>
          </label>
          <label class="recommend-option flex-1">
            <input type="radio" name="would_recommend" value="no" class="sr-only">
            <span class="recommend-btn no flex items-center justify-center gap-2 rounded-lg border-2 border-on-surface/20 bg-white px-5 py-3 font-black text-sm cursor-pointer transition-all hover:border-on-surface w-full">
              👎 Not really
            </span>
          </label>
        </div>
      </div>
    </div>

    <!-- Step 3 -->
    <div class="card-hard p-8 relative">
      <div class="absolute -top-4 -left-4 h-10 w-10 bg-rye-red text-white border-2 border-on-surface rounded-full flex items-center justify-center font-black text-xl shadow-hard-sm">3</div>
      <h3 class="text-xl font-black mb-6">Tell Future Students</h3>

      <div class="mb-6">
        <label class="block text-xs font-black uppercase mb-2 tracking-wider">Review Headline <span class="text-on-surface/40">(optional)</span></label>
        <input type="text" name="title" placeholder='e.g. "Brutal but worth every second."'
               class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2.5 px-4 text-sm font-medium focus:border-on-surface outline-none transition-all">
      </div>

      <div class="mb-6">
        <label class="block text-xs font-black uppercase mb-2 tracking-wider">Overall Experience</label>
        <p class="text-[10px] text-on-surface/40 mb-2 font-bold">What was the class really like? What did you enjoy or find tough?</p>
        <textarea name="review_text" rows="4"
                  placeholder="Share your honest experience — the good, the bad, and everything in between…"
                  class="w-full rounded-lg border-2 border-on-surface/20 bg-surface p-4 text-sm font-medium focus:border-on-surface outline-none resize-y min-h-[100px]"></textarea>
      </div>

      <div class="mb-6">
        <label class="block text-xs font-black uppercase mb-2 tracking-wider">Advice for Future Students</label>
        <p class="text-[10px] text-on-surface/40 mb-2 font-bold">What's the secret to doing well? Tips on projects, exams, or how to get on the teacher's good side.</p>
        <textarea name="advice" rows="3"
                  placeholder="e.g. Start DBQ practice early, form a study group, don't skip the textbook…"
                  class="w-full rounded-lg border-2 border-on-surface/20 bg-surface p-4 text-sm font-medium focus:border-on-surface outline-none resize-y min-h-[80px]"></textarea>
      </div>

      <div>
        <label class="block text-xs font-black uppercase mb-2 tracking-wider">Materials Used</label>
        <p class="text-[10px] text-on-surface/40 mb-3 font-bold">Select all that apply.</p>
        <div class="flex flex-wrap gap-2 mb-3">
          {% for mat in materials_options %}
          <label class="material-chip">
            <input type="checkbox" name="materials" value="{{ mat }}" class="sr-only">
            <span class="flex items-center gap-1.5 rounded-full border-2 border-on-surface/20 bg-white px-4 py-2 text-xs font-black cursor-pointer transition-all hover:border-on-surface select-none">
              {{ mat }}
            </span>
          </label>
          {% endfor %}
        </div>
        <input type="text" name="materials_other" placeholder="Other materials (optional)…"
               class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2 px-4 text-sm font-medium focus:border-on-surface outline-none transition-all mt-2">
      </div>
    </div>

    <div class="flex flex-col sm:flex-row justify-end gap-4 pb-16">
      <a href="{{ url_for('course_detail', course_id=course.id) }}"
         class="rounded-lg border-2 border-on-surface bg-white px-8 py-3 font-black btn-hard text-sm text-center">Cancel</a>
      <button type="submit"
              class="rounded-lg border-2 border-on-surface bg-rye-red px-12 py-3 text-lg font-black text-white btn-hard">
        Post Review
      </button>
    </div>
  </form>
</div>
{% endblock %}

{% block scripts %}
<script>
const ratingDescs = {
  overall:       ['', 'Terrible', 'Poor', 'Okay', 'Good', 'Amazing'],
  teacher_rating:['', 'Very Poor', 'Below Average', 'Average', 'Good', 'Excellent'],
  workload:      ['', 'Very Light', 'Light', 'Moderate', 'Heavy', 'Very Heavy'],
};

document.querySelectorAll('.star-picker').forEach(picker => {
  const name  = picker.dataset.name;
  const stars = picker.querySelectorAll('.star-pick');
  const input = picker.querySelector('input[type=hidden]');
  const desc  = document.getElementById(name + '-desc');
  let selected = 0;
  const paint = val => {
    stars.forEach(s => s.classList.toggle('active', +s.dataset.val <= val));
    if (desc && ratingDescs[name]) desc.textContent = val ? ratingDescs[name][val] : '';
  };
  stars.forEach(star => {
    star.addEventListener('mouseenter', () => paint(+star.dataset.val));
    star.addEventListener('mouseleave', () => paint(selected));
    star.addEventListener('click', () => { selected = +star.dataset.val; input.value = selected; paint(selected); });
  });
});

const diffInput = document.getElementById('difficulty');
const diffDisplay = document.getElementById('difficulty-display');
document.querySelectorAll('.diff-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const val = +btn.dataset.val;
    diffInput.value = val;
    diffDisplay.innerHTML = val + '<span class="text-on-surface/40 text-lg">/5</span>';
    document.querySelectorAll('.diff-btn').forEach(b => {
      b.classList.toggle('bg-rye-red', +b.dataset.val === val);
      b.classList.toggle('text-white', +b.dataset.val === val);
      b.classList.toggle('bg-white', +b.dataset.val !== val);
      b.classList.toggle('text-on-surface', +b.dataset.val !== val);
    });
  });
});

document.querySelectorAll('.recommend-option').forEach(label => {
  label.querySelector('input').addEventListener('change', () => {
    document.querySelectorAll('.recommend-btn').forEach(btn => {
      btn.classList.remove('bg-emerald-50','border-emerald-400','text-emerald-700','bg-red-50','border-red-400','text-red-700','border-on-surface');
      btn.classList.add('border-on-surface/20');
    });
    const btn = label.querySelector('.recommend-btn');
    btn.classList.remove('border-on-surface/20');
    if (label.querySelector('input').value === 'yes') btn.classList.add('bg-emerald-50','border-emerald-400','text-emerald-700');
    else btn.classList.add('bg-red-50','border-red-400','text-red-700');
  });
});

document.querySelectorAll('.material-chip').forEach(label => {
  const input = label.querySelector('input');
  const span  = label.querySelector('span');
  input.addEventListener('change', () => {
    span.classList.toggle('border-on-surface', input.checked);
    span.classList.toggle('bg-on-surface', input.checked);
    span.classList.toggle('text-white', input.checked);
    span.classList.toggle('border-on-surface/20', !input.checked);
  });
});

document.getElementById('reviewForm').addEventListener('submit', e => {
  for (const name of ['overall', 'difficulty', 'teacher_rating', 'workload']) {
    if (!document.getElementById(name).value) {
      e.preventDefault();
      const el = document.querySelector('[data-name="' + name + '"]') || document.getElementById(name);
      if (el) { el.scrollIntoView({ behavior: 'smooth', block: 'center' }); el.style.outline = '3px solid #b61722'; el.style.outlineOffset = '4px'; el.style.borderRadius = '8px'; setTimeout(() => { el.style.outline = ''; }, 2000); }
      return;
    }
  }
});
</script>
{% endblock %}"""

ADD_COURSE_HTML = """{% extends "base.html" %}
{% block title %}Add a Course — Garnet Network{% endblock %}
{% block content %}
<div class="max-w-2xl mx-auto">

  <a href="{{ url_for('directory') }}" class="inline-flex items-center gap-1.5 text-sm font-black text-on-surface/60 hover:text-rye-red transition-colors mb-8">
    <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
    Back to Directory
  </a>

  <div class="mb-10">
    <h1 class="text-4xl font-black mb-2 tracking-tighter">Add a Class</h1>
    <p class="text-lg text-on-surface/60 font-medium">Don't see a course in the directory? Add it so students can start leaving reviews.</p>
  </div>

  <form method="POST" class="flex flex-col gap-6">
    <div class="card-hard p-8">
      <h2 class="text-lg font-black mb-6 border-b-2 border-on-surface pb-2">Course Information</h2>

      <div class="mb-5">
        <label class="block text-xs font-black uppercase mb-2 tracking-wider">Course Name <span class="text-rye-red">*</span></label>
        <input type="text" name="name" required
               placeholder="e.g. AP Calculus BC, Honors Chemistry, Film as Literature"
               class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2.5 px-4 font-medium text-sm focus:border-on-surface outline-none transition-all">
      </div>

      <div class="grid grid-cols-2 gap-4 mb-5">
        <div>
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Course Code <span class="text-on-surface/40 font-normal">(optional)</span></label>
          <input type="text" name="code" placeholder="e.g. 0341"
                 class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2.5 px-4 font-medium text-sm focus:border-on-surface outline-none transition-all">
        </div>
        <div>
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Course Type</label>
          <select name="course_type" class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2.5 px-4 font-medium text-sm focus:border-on-surface outline-none">
            {% for t in course_types %}<option value="{{ t }}">{{ t }}</option>{% endfor %}
          </select>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4 mb-5">
        <div>
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Department</label>
          <select name="department" class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2.5 px-4 font-medium text-sm focus:border-on-surface outline-none">
            <option value="">Select department</option>
            {% for d in departments %}<option value="{{ d }}">{{ d }}</option>{% endfor %}
          </select>
        </div>
        <div>
          <label class="block text-xs font-black uppercase mb-2 tracking-wider">Grade Levels</label>
          <input type="text" name="grades" placeholder="e.g. 9–12 or 11, 12"
                 class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2.5 px-4 font-medium text-sm focus:border-on-surface outline-none transition-all">
        </div>
      </div>

      <div class="mb-5">
        <label class="block text-xs font-black uppercase mb-2 tracking-wider">Credits</label>
        <input type="text" name="credits" placeholder="e.g. 1 or ½"
               class="w-full rounded-lg border-2 border-on-surface/20 bg-surface py-2.5 px-4 font-medium text-sm focus:border-on-surface outline-none transition-all">
      </div>

      <div>
        <label class="block text-xs font-black uppercase mb-2 tracking-wider">Description <span class="text-on-surface/40 font-normal">(optional)</span></label>
        <textarea name="description" rows="4"
                  placeholder="Brief description of what the course covers…"
                  class="w-full rounded-lg border-2 border-on-surface/20 bg-surface p-4 font-medium text-sm focus:border-on-surface outline-none resize-y"></textarea>
      </div>
    </div>

    <div class="flex justify-end gap-4 pb-16">
      <a href="{{ url_for('directory') }}"
         class="rounded-lg border-2 border-on-surface bg-white px-8 py-3 font-black btn-hard text-sm">Cancel</a>
      <button type="submit"
              class="rounded-lg border-2 border-on-surface bg-rye-red px-10 py-3 font-black text-white btn-hard text-sm">
        Add Class
      </button>
    </div>
  </form>
</div>
{% endblock %}"""

# ─── App setup ────────────────────────────────────────────────────────────────

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classrate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'ryehigh-classrate-2024'

app.jinja_loader = DictLoader({
    'base.html':          BASE_HTML,
    'index.html':         INDEX_HTML,
    'directory.html':     DIRECTORY_HTML,
    'course_detail.html': COURSE_DETAIL_HTML,
    'add_review.html':    ADD_REVIEW_HTML,
    'add_course.html':    ADD_COURSE_HTML,
})

db = SQLAlchemy(app)

# ─── Models ───────────────────────────────────────────────────────────────────

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(20))
    department = db.Column(db.String(100))
    course_type = db.Column(db.String(30))
    grades = db.Column(db.String(50))
    credits = db.Column(db.String(10))
    description = db.Column(db.Text)
    reviews = db.relationship('Review', backref='course', lazy=True, cascade='all, delete-orphan')

    @property
    def avg_overall(self):
        if not self.reviews: return 0
        return round(sum(r.overall for r in self.reviews) / len(self.reviews), 1)

    @property
    def avg_difficulty(self):
        if not self.reviews: return 0
        return round(sum(r.difficulty for r in self.reviews) / len(self.reviews), 1)

    @property
    def avg_teacher(self):
        if not self.reviews: return 0
        return round(sum(r.teacher_rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def avg_workload(self):
        if not self.reviews: return 0
        return round(sum(r.workload for r in self.reviews) / len(self.reviews), 1)

    @property
    def review_count(self):
        return len(self.reviews)

    @property
    def recommend_pct(self):
        if not self.reviews: return 0
        return round(sum(1 for r in self.reviews if r.would_recommend) / len(self.reviews) * 100)

    @property
    def difficulty_label(self):
        d = self.avg_difficulty
        if d == 0: return None
        if d < 2: return 'Easy'
        if d < 3.5: return 'Medium'
        return 'Hard'


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    author = db.Column(db.String(100), default='Anonymous')
    grade_level = db.Column(db.String(20))
    grade_earned = db.Column(db.String(5))
    semester = db.Column(db.String(30))
    title = db.Column(db.String(200))
    overall = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    teacher_rating = db.Column(db.Integer, nullable=False)
    workload = db.Column(db.Integer, nullable=False)
    would_recommend = db.Column(db.Boolean, default=True)
    review_text = db.Column(db.Text)
    advice = db.Column(db.Text)
    materials = db.Column(db.Text)
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


DEPARTMENTS = [
    'Art & Design', 'English', 'Health & PE', 'Mathematics',
    'Music', 'Occupational Education', 'Science', 'Social Studies',
    'STEM / Engineering', 'Computer Science', 'Theater Arts', 'World Language'
]
COURSE_TYPES = ['Regular', 'Honors', 'AP', 'Elective', 'Seminar']
GRADE_LEVELS = ['9th Grade', '10th Grade', '11th Grade', '12th Grade']
GRADES_EARNED = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F']
SEMESTERS = ['Fall 2024', 'Spring 2024', 'Fall 2023', 'Spring 2023', 'Fall 2022', 'Spring 2022']
MATERIALS_OPTIONS = ['Textbook', 'Online Modules', 'Lab Kit', 'Custom Packet', 'Graphing Calculator',
                     'Sketchbook', 'Lab Notebook', 'Binder / Notebook', 'None']

# ─── Context processor ────────────────────────────────────────────────────────

@app.context_processor
def inject_courses_for_modal():
    return dict(all_courses_for_modal=Course.query.order_by(Course.name).all())

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(8).all()
    total_reviews = Review.query.count()
    total_courses = Course.query.count()
    all_ratings = [r.overall for r in Review.query.all()]
    avg_rating = round(sum(all_ratings) / len(all_ratings), 1) if all_ratings else 0
    trending = sorted(
        [c for c in Course.query.all() if c.review_count > 0],
        key=lambda c: c.review_count, reverse=True
    )[:3]
    return render_template('index.html',
        recent_reviews=recent_reviews, total_reviews=total_reviews,
        total_courses=total_courses, avg_rating=avg_rating, trending=trending)


@app.route('/directory')
def directory():
    search = request.args.get('search', '').strip()
    dept = request.args.get('dept', '')
    sort = request.args.get('sort', 'name')
    course_type = request.args.get('type', '')

    query = Course.query
    if search:
        query = query.filter(db.or_(
            Course.name.ilike(f'%{search}%'),
            Course.code.ilike(f'%{search}%'),
        ))
    if dept:
        query = query.filter(Course.department == dept)
    if course_type:
        query = query.filter(Course.course_type == course_type)

    courses = query.all()
    if sort == 'rating':
        courses.sort(key=lambda c: c.avg_overall, reverse=True)
    elif sort == 'difficulty_high':
        courses.sort(key=lambda c: c.avg_difficulty, reverse=True)
    elif sort == 'difficulty_low':
        courses.sort(key=lambda c: (c.avg_difficulty if c.avg_difficulty > 0 else 99))
    elif sort == 'reviews':
        courses.sort(key=lambda c: c.review_count, reverse=True)
    else:
        courses.sort(key=lambda c: c.name)

    return render_template('directory.html',
        courses=courses, departments=DEPARTMENTS, course_types=COURSE_TYPES,
        search=search, dept=dept, sort=sort, course_type=course_type)


@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    reviews = Review.query.filter_by(course_id=course_id).order_by(Review.created_at.desc()).all()
    return render_template('course_detail.html', course=course, reviews=reviews)


@app.route('/course/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course = Course(
            name=request.form['name'].strip(),
            code=request.form.get('code', '').strip(),
            department=request.form.get('department', ''),
            course_type=request.form.get('course_type', 'Regular'),
            grades=request.form.get('grades', '').strip(),
            credits=request.form.get('credits', '').strip(),
            description=request.form.get('description', '').strip()
        )
        db.session.add(course)
        db.session.commit()
        return redirect(url_for('course_detail', course_id=course.id))
    return render_template('add_course.html', departments=DEPARTMENTS, course_types=COURSE_TYPES)


@app.route('/course/<int:course_id>/review', methods=['GET', 'POST'])
def add_review(course_id):
    course = Course.query.get_or_404(course_id)
    error = request.args.get('error')
    if request.method == 'POST':
        materials_list = request.form.getlist('materials')

        # Fields to moderate
        title       = request.form.get('title', '').strip()
        review_text = request.form.get('review_text', '').strip()
        advice      = request.form.get('advice', '').strip()
        author      = request.form.get('author', '').strip() or 'Anonymous'

        # Run AI moderation
        allowed, reason = moderate_review(course.name, author, title, review_text, advice)
        if not allowed:
            return redirect(url_for('add_review', course_id=course_id, error=reason))

        # All clean — save the review as-is
        review = Review(
            course_id=course_id,
            author=author,
            grade_level=request.form.get('grade_level', ''),
            grade_earned=request.form.get('grade_earned', ''),
            semester=request.form.get('semester', ''),
            title=title,
            overall=int(request.form['overall']),
            difficulty=int(request.form['difficulty']),
            teacher_rating=int(request.form['teacher_rating']),
            workload=int(request.form['workload']),
            would_recommend=request.form.get('would_recommend') == 'yes',
            review_text=review_text,
            advice=advice,
            materials=', '.join(materials_list) if materials_list else request.form.get('materials_other', '').strip(),
        )
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('course_detail', course_id=course_id))
    return render_template('add_review.html', course=course,
        grade_levels=GRADE_LEVELS, grades_earned=GRADES_EARNED,
        semesters=SEMESTERS, materials_options=MATERIALS_OPTIONS, error=error)


@app.route('/review/<int:review_id>/like', methods=['POST'])
def like_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.likes += 1
    db.session.commit()
    return jsonify({'likes': review.likes})


@app.route('/review/<int:review_id>/delete', methods=['POST'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    course_id = review.course_id
    db.session.delete(review)
    db.session.commit()
    return redirect(url_for('course_detail', course_id=course_id))


@app.route('/course/<int:course_id>/delete', methods=['POST'])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for('directory'))

# ─── Seed data ────────────────────────────────────────────────────────────────

def seed_data():
    if Course.query.count() > 0:
        return

    courses = [
        # Art & Design
        Course(name='Studio Art: Painting & Drawing', code='0909A', department='Art & Design', course_type='Elective', grades='9–12', credits='½', description='A well-rounded introduction to 2D media techniques: color theory, drawing from observation, linear perspective, and graphic design. Culminates in a student-curated digital gallery.'),
        Course(name='Studio Art: Mixed Media', code='0913', department='Art & Design', course_type='Elective', grades='9–12', credits='½', description='Explores sculpture, 3D design, ceramics, printmaking, and digital/paper collage. Students build a portfolio of work across a range of materials and techniques.'),
        Course(name='Studio Art: Digital Media', code='0914', department='Art & Design', course_type='Elective', grades='9–12', credits='½', description='Image-making using contemporary digital tools. Students learn digital photography fundamentals and Adobe Photoshop, completing themed image series and group critiques.'),
        Course(name='Studio Art: Graphic Design & Animation', code='0925A', department='Art & Design', course_type='Elective', grades='9–12', credits='½', description='Real-world applications of 2D design and animation using Adobe Photoshop. Students create a logo, product proposal, and animated advertisement as part of a capstone campaign.'),
        Course(name='AP Studio Art: 2D Design', code='0918', department='Art & Design', course_type='AP', grades='11–12', credits='1', description='Students build a college-level 2D portfolio submitted to the College Board, covering graphic design, photography, painting, and printmaking. Equivalent to a one-semester intro college design course.'),
        Course(name='AP Studio Art: Drawing', code='0922', department='Art & Design', course_type='AP', grades='11–12', credits='1', description='Students develop a portfolio meeting college-level standards, mastering composition, concentration, and presentation. Work is submitted to College Board for review by art scholars.'),
        Course(name='Ceramics', code='0903', department='Art & Design', course_type='Elective', grades='10–12', credits='½', description='An introduction to pottery by hand and by wheel. Students study historical ceramics, decorating techniques, underglazes, and the relationship between form and function.'),
        Course(name='Yearbook Journalism', code='0144', department='Art & Design', course_type='Elective', grades='11–12', credits='1', description='Students plan and produce the RHS yearbook: writing copy, creating layouts, taking photos, and meeting real production deadlines. Leadership and creativity are central to the course.'),
        # English
        Course(name='English 9', code='0103', department='English', course_type='Regular', grades='9', credits='1', description='Students develop skills to interpret sophisticated prose through close examination of literary texts, including Romeo and Juliet, The Catcher in the Rye, and Lord of the Flies, alongside formal essay writing.'),
        Course(name='Composition', code='0104', department='English', course_type='Regular', grades='9', credits='½', description='A required half-credit writing course for 9th graders. Ranges from descriptive and narrative work to argumentative essays, with peer editing and grammar taught in context.'),
        Course(name='English 10', code='0109', department='English', course_type='Regular', grades='10', credits='1', description='Explores four thematic centers — perspective, empathy, roles in society, and citizenship — through texts like The Kite Runner, Of Mice and Men, and Night.'),
        Course(name='English 11', code='0122', department='English', course_type='Regular', grades='11', credits='1', description='Enhances critical reading and writing skills through the American experience. Core texts include The Things They Carried, The Crucible, and The Great Gatsby.'),
        Course(name='AP Language & Composition', code='0118', department='English', course_type='AP', grades='11–12', credits='1', description='A year-long course focused on nonfiction and the essay as a literary genre. Includes In Cold Blood, Educated, and Killers of the Flower Moon. Rigorous analytical writing throughout.'),
        Course(name='AP Literature & Composition', code='0130', department='English', course_type='AP', grades='11–12', credits='1', description='For students with exceptional ability in reading and writing. Engages works across genres, time periods, and cultures, developing sophisticated writers who use language to inform and engage.'),
        Course(name='Film as Literature', code='0129', department='English', course_type='Elective', grades='12', credits='½', description='Students study film history, techniques, and terminology, analyzing how filmmakers create meaning through dialogue, camera angles, lighting, and more. Includes original short film projects.'),
        Course(name='Creative Writing', code='0138', department='English', course_type='Elective', grades='12', credits='½', description='A writing workshop course where students write personal narratives, short stories, poetry, and film scripts. Only those serious about writing should enroll — intensive peer critique throughout.'),
        Course(name='Public Speaking & Debate', code='0152', department='English', course_type='Elective', grades='12', credits='½', description='Builds confidence and competence in public speaking, persuasion, and critical listening. Students analyze famous speeches and participate in structured debate rounds.'),
        Course(name='Introduction to Journalism', code='0147', department='English', course_type='Elective', grades='10–12', credits='½', description='Covers journalistic writing, interviewing, reporting, and media ethics across print, web, podcast, and video formats. Students develop essential skills for reliable, independent reporting.'),
        Course(name='AP Seminar', code='0159', department='English', course_type='AP', grades='10–11', credits='1', description='First course in the AP Capstone diploma. Students explore academic and real-world issues by analyzing multiple perspectives, conducting research, and communicating ideas orally and in writing.'),
        # Mathematics
        Course(name='Algebra 1', code='0300', department='Mathematics', course_type='Regular', grades='9', credits='1', description='Follows NYS Next Generation Learning Standards. In-depth study of algebraic relationships: linear, quadratic, and exponential functions, systems of equations, probability, and statistics. Includes Regents exam.'),
        Course(name='Algebra 2R Enhanced', code='0302', department='Mathematics', course_type='Regular', grades='9–10', credits='1', description='Comprehensively covers quadratic functions, polynomial and rational expressions, exponential/logarithmic functions, sequences, and statistics. More in-depth exploration than standard Algebra 2R.'),
        Course(name='Algebra 2 Enhanced Honors', code='0303', department='Mathematics', course_type='Honors', grades='9–10', credits='1', description='Advanced Algebra 2 covering topics in a rigorous, rapid environment, with PreCalculus concepts woven in. Requires exceptional performance in Algebra 1 and teacher recommendation.'),
        Course(name='Geometry / Trigonometry Enhanced', code='0327', department='Mathematics', course_type='Regular', grades='10–11', credits='1', description='Covers geometric terms, theorems, formal proofs, and a thorough introduction to trigonometric functions including the Unit Circle, Law of Sines, Law of Cosines, and trig identities.'),
        Course(name='Geometry / Trigonometry Enhanced Honors', code='0328', department='Mathematics', course_type='Honors', grades='10–11', credits='1', description='Advanced Geo/Trig course in a rigorous and rapid setting, incorporating PreCalculus concepts. Requires mastery of Algebra 2 Honors and teacher recommendation. Fast-paced and demanding.'),
        Course(name='Pre-Calculus', code='0333', department='Mathematics', course_type='Regular', grades='11–12', credits='1', description='Covers functions, conic sections, limits, higher-degree equations, matrices, and trigonometry. Graphing calculator required. Prepares students for calculus coursework.'),
        Course(name='Pre-AP Calculus', code='0334', department='Mathematics', course_type='Regular', grades='11–12', credits='1', description='Designed for students planning to take AP Calculus AB. Includes college-level algebra, function theory, exponentials, logarithms, circular functions, conic sections, and derivatives.'),
        Course(name='Pre-AP Calculus Honors', code='0335', department='Mathematics', course_type='Honors', grades='11', credits='1', description='Covers PreCalculus in the first semester and begins the AP Calculus AB curriculum in the second. Requires exceptional performance in Geo/Trig Honors and teacher recommendation.'),
        Course(name='Contemporary Mathematics', code='0349', department='Mathematics', course_type='Regular', grades='11–12', credits='1', description='Designed for students seeking real-world math applications: personal finance, problem-solving, statistics, and probability. Available for dual enrollment with SUNY Westchester Community College.'),
        Course(name='AP Statistics', code='0339', department='Mathematics', course_type='AP', grades='11–12', credits='1', description='Covers exploring data, planning studies, anticipating patterns, and statistical inference. Students develop skills for collecting, analyzing, and drawing conclusions from data.'),
        Course(name='AP Calculus AB', code='0340', department='Mathematics', course_type='AP', grades='11–12', credits='1', description='College-level calculus covering limits, derivatives, integrals, and the Fundamental Theorem of Calculus. Strong emphasis on conceptual understanding and multiple representations of functions.'),
        Course(name='AP Calculus BC', code='0341', department='Mathematics', course_type='AP', grades='11–12', credits='1', description='Extension of Calculus AB covering parametric equations, polar coordinates, vector-valued functions, and infinite series. One of the most rigorous math courses offered at RHS.'),
        # Science
        Course(name='Life Science: Biology', code='0362A', department='Science', course_type='Regular', grades='9', credits='1', description='Meets NYS Science Learning Standards. Covers homeostasis, genetics, photosynthesis, reproduction, evolution, and ecology through phenomena-based investigation and lab experiments.'),
        Course(name='Life Science: Biology Honors', code='0360A', department='Science', course_type='Honors', grades='9', credits='1', description='More advanced and mathematical than standard Biology. Covers biochemical pathways, cellular processes, genetics, and ecology in greater depth. Students must have a 95 in Science 8 or 90 in Regents Earth Science.'),
        Course(name='Earth & Space Sciences', code='0390A', department='Science', course_type='Regular', grades='10–11', credits='1', description='Covers geology, meteorology, astronomy, and oceanography aligned with NYSED standards. Field trips and labs are central to the course experience.'),
        Course(name='Honors Chemistry', code='0371', department='Science', course_type='Honors', grades='10–11', credits='1', description='In-depth study of matter, chemical reactions, stoichiometry, thermodynamics, and atomic theory. Heavy laboratory component. One of the most demanding science courses at RHS.'),
        Course(name='AP Biology', code='0386', department='Science', course_type='AP', grades='11–12', credits='1', description='Rigorous, fast-paced course requiring strong work ethic and independent analysis. Combines inquiry-based labs with scientific practices: explaining, evaluating, predicting, and mathematical computation. Minimum 6 hrs/week outside class.'),
        Course(name='AP Chemistry', code='0387', department='Science', course_type='AP', grades='11–12', credits='1', description='College-level chemistry covering atomic structure, bonding, thermodynamics, kinetics, and electrochemistry. Lab-intensive with substantial written analysis. Requires strong math foundation.'),
        Course(name='AP Physics 1', code='0375', department='Science', course_type='AP', grades='11–12', credits='1', description='Algebra-based physics covering kinematics, dynamics, rotation, energy, waves, and circuits. Inquiry-based with significant lab work and a focus on reasoning from evidence.'),
        Course(name='Science & Society', code='0384', department='Science', course_type='Elective', grades='11–12', credits='1', description='In-depth look at various biology and interdisciplinary science topics selected by teacher and students: human physiology, nutrition, marine biology, environmental science, and more. Predominantly project-based.'),
        # Social Studies
        Course(name='Global History 9', code='0201', department='Social Studies', course_type='Regular', grades='9', credits='1', description='In-depth study of world history from the rise of early civilizations to 1750. Emphasizes written/oral expression, research, critical thinking, and analysis of primary source documents.'),
        Course(name='Global History 10', code='0209', department='Social Studies', course_type='Regular', grades='10', credits='1', description='World history from 1750 to the present, including geographic reasoning, gathering and interpreting evidence, and critical thinking. Includes the NYS Global History & Geography II Regents exam.'),
        Course(name='AP World History', code='0235', department='Social Studies', course_type='AP', grades='10', credits='1', description='College-level study of global history from 1200 CE to the present, across six world regions. Heavy emphasis on analytical writing, DBQs, LEQs, and primary/secondary source analysis.'),
        Course(name='AP U.S. History', code='0222', department='Social Studies', course_type='AP', grades='11', credits='1', description="Rigorous college-level survey of American history, emphasizing historical thinking skills, DBQs, and analytical writing. One of the most work-intensive courses at RHS — Henderson's review sessions are legendary."),
        Course(name='AP Psychology', code='0260', department='Social Studies', course_type='AP', grades='11–12', credits='1', description='Introductory college-level psychology covering biological bases of behavior, sensation, learning, cognition, developmental psychology, and social psychology.'),
        Course(name='Participation in Government', code='0231', department='Social Studies', course_type='Regular', grades='12', credits='½', description='Required half-credit course meeting NYS requirements. Students examine the structure of government, civic participation, and current political issues through debate and project-based learning.'),
        Course(name='Economics', code='0240', department='Social Studies', course_type='Regular', grades='12', credits='½', description='Meets NYS Economics requirement. Studies microeconomics, macroeconomics, personal finance, and global economic systems. Real-world applications and current events are central.'),
        # Computer Science
        Course(name='Computer Science Essentials', code='0541', department='Computer Science', course_type='Elective', grades='9–12', credits='½', description='Entry-level CS course. Students progress from block-based programming to Python, building apps and exploring computational thinking. Great for students new to coding.'),
        Course(name='Computer Science Cybersecurity', code='0542', department='Computer Science', course_type='Elective', grades='10–12', credits='½', description='Exposes students to cybersecurity through problem-based, role-play scenarios as cybersecurity experts. Connects to the NICE Framework standards used by the federal government.'),
        Course(name='AP Computer Science Principles', code='0348', department='Computer Science', course_type='AP', grades='10–12', credits='1', description='Inquiry-based exploration of core computing concepts: programming, algorithms, data, the internet, and societal impact. Students solve problems individually and collaboratively.'),
        Course(name='AP Computer Science A', code='0396', department='Computer Science', course_type='AP', grades='11–12', credits='1', description='Programming methodology using Java, including algorithms, data structures, and data abstraction. Minimum 8 hours of outside work per week. Prepares students for the AP CS A exam.'),
        # Theater
        Course(name='Introduction to Theater', code='0800', department='Theater Arts', course_type='Elective', grades='9–12', credits='½', description='Foundational theater course covering acting techniques, voice and movement, improvisation, and scene work. Students develop confidence performing for an audience.'),
        Course(name='Advanced Theater / Drama', code='0802', department='Theater Arts', course_type='Elective', grades='10–12', credits='1', description='Advanced acting, directing, and technical theater skills. Students participate in full-scale productions. Strong emphasis on collaboration, discipline, and stage presence.'),
        # World Languages
        Course(name='Spanish 1', code='0701', department='World Language', course_type='Regular', grades='9–12', credits='1', description='Introductory Spanish with focus on foundational grammar, vocabulary, and basic conversation in real-world contexts.'),
        Course(name='AP Spanish Language & Culture', code='0718', department='World Language', course_type='AP', grades='11–12', credits='1', description="College-level Spanish developing interpersonal, interpretive, and presentational communication skills. Eligible for dual enrollment via St. John's University College Advantage."),
        Course(name='AP French Language & Culture', code='0728', department='World Language', course_type='AP', grades='11–12', credits='1', description="College-level French developing all modes of communication. Eligible for dual enrollment via St. John's University College Advantage program."),
        Course(name='Mandarin 5 / 5 Honors', code='0760', department='World Language', course_type='Regular', grades='11–12', credits='1', description="Advanced Mandarin Chinese covering complex conversation, reading, and writing. Eligible for dual enrollment via St. John's University College Advantage."),
    ]
    db.session.add_all(courses)
    db.session.commit()



def purge_inappropriate_reviews():
    """Delete any existing reviews that contain profanity."""
    all_reviews = Review.query.all()
    deleted = 0
    for review in all_reviews:
        combined = ' '.join(filter(None, [
            review.title or '',
            review.review_text or '',
            review.advice or '',
            review.author or '',
        ]))
        if profanity.contains_profanity(combined):
            db.session.delete(review)
            deleted += 1
    if deleted:
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_data()
    purge_inappropriate_reviews()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=False)
