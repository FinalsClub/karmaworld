import json
from notes.models import *

def school_to_dict(school):
    """Convert School -> Dict"""
    s_dict = school.__dict__
    school_dict = {}
    
    school_dict['name'] = s_dict['name']
    school_dict['slug'] = s_dict['slug']
    school_dict['location'] = s_dict['location']
    school_dict['url'] = s_dict['url']
    school_dict['facebook_id'] = s_dict['facebook_id']
    school_dict['id'] = s_dict['id']
    return school_dict


def course_to_dict(course):
    """Convert Course -> Dict"""
    c_dict = course.__dict__
    course_dict = {}

    course_dict['name'] = c_dict['title']
    course_dict['slug'] = c_dict['slug']
    course_dict['school_id'] = c_dict['school_id']
    course_dict['desc'] = c_dict['desc']
    course_dict['url'] = c_dict['url']
    course_dict['academic_year'] = c_dict['academic_year']
    try:
    	course_dict['instructor_name'] = course.instructor.name
    except AttributeError:
    	course_dict['instructor_name'] = ''
    try:
	course_dict['instructor_email'] = course.instructor.email
    except AttributeError:
	course_dict['instructor_email'] = ''
#    course_dict['instructor_email']
    course_dict['updated_at'] = str(c_dict['last_updated'])
    course_dict['id'] = c_dict['id']
    return course_dict

def note_to_dict(note):
    """Convert Note -> Dict"""
    n_dict = note.__dict__
    notes_dict = {}

    notes_dict['course_id'] = n_dict['course_id']
    notes_dict['tags'] = [tag.name for tag in note.tags.all()]
    notes_dict['name'] = n_dict['title']
    notes_dict['desc'] = n_dict['description']
    notes_dict['uploaded_at'] = str(n_dict['timestamp'])
#   notes_dict['file_type']
#   notes_dict['note_file'] 
    notes_dict['embed_url'] = n_dict['embed_url']
#   notes_dict['download_url']
    notes_dict['html'] = n_dict['html']
    notes_dict['text'] = n_dict['text']
    notes_dict['file_path'] = n_dict['file']
    notes_dict['id'] = n_dict['id']

    return notes_dict
