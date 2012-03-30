#RGS Scheduler
#By Nick Hershman

#Global statics
BOY = 'b'
GIRL = 'g'

SS = 'Social Studies'
SCI = 'Science'
MATH = 'Math'
LA = 'Language Arts'
SP = 'Spanish'
E = 'Elective'

SUBJECTS=[SS, SCI, MATH, LA, SP] #The subjects to schedule

TEACHERS = [
    ['Hershman','Nick',MATH],
    ['Robinson','Jeff',SS],
    ['Leve','Jill',SCI],
    ['Dawes','Angela',SP],
    ['Mandis','Bill',LA],
    ['Reece','Larissa',MATH],
    ['Black','Brian',LA],
    ['Nebert','Dietrich',SCI]
    ]

MATH_COURSES = [
    'pre-algebra',
    'algebra',
    'geo',
    'algebra II',
    ]

#[TODO: thinking about a potential bug...
#How to treat math classes?

class Student(object):

    def __init__(self,first,last,gender,grade,homeroom,math_level=None):
        self.first = first
        self.last = last
        self.gender = gender
        self.grade = grade
        self.homeroom = homeroom
        self.math_level = math_level
        self.schedule = {}
        self.subjects_enrolled = []

    def update(self):
        self.subjects_enrolled = []
        for i in self.schedule.values():
            sub = ''
            if i.subject in SUBJECTS: sub = i.subject
            elif i.subject in MATH_COURSES: sub = MATH
            else: raise Exception('Invalid subject for',self)
            self.subjects_enrolled.append(sub)

    def is_free(self, period):
        try:
            self.schedule[int(period)]
        except KeyError:
            return True
        return False

    def has_subject(self, subject):
        if subject in SUBJECTS:
            if subject in self.subjects_enrolled: return True
            else: return False
        else:
            if subject in MATH_COURSES:
                if MATH in self.subjects_enrolled: return True
                else: return False
        return False

    def could_take_course(self,course):
        """ Returns True if the student already has the subject of the course """
        #if course.count() >= course.max_size: return False
        if course.subject in SUBJECTS:
            if not course.subject in self.subjects_enrolled and self.is_free(course.period): return True
            else: return False
        else:
            if course.subject in MATH_COURSES:
                if not MATH in self.subjects_enrolled and self.is_free(course.period): return True
                else: return False
        return False
        print 'Error finding subject in students courses.. for course:',course,'of subject:',course.subject

    def get_valid_courses(self, courses):
        match = []
        for i in courses:
            if not self.has_subject(i.subject) and self.grade in i.for_grades: match.append(i)
        return match   

    def get_subject_courses(self, subject, courses):
        """ Using the list of courses, select all courses that match the subject at student's grade level"""
        match = []
        for i in courses:
            if subject == i.subject and self.grade in i.for_grades: match.append(i)
            if subject == MATH and i.subject == self.math_level: match.append(i)
        return match

    def add_course(self,course,):
        if not self.grade in course.for_grades: raise Exception('%s is not at %s\'s grade level and will not be added.' % (course, self.first))
        if self.is_free(course.period) and self.could_take_course(course):
            self.schedule[int(course.period)] = course
            course.add_student(self)
            self.update()
            #print self,'added to:',course,'with',course.count(),'students.'
            #print type(course)
            return True
        else:
            return False

    def rem_course(self, period):
        if not self.is_free(period):
            del self.schedule[period]
            self.update()
            return True
        else:
            return False

    def clear_schedule(self):
        for i in self.schedule.values():
            i.rem_student(self)
        self.schedule.clear()       
        self.update()

    def __str__(self):
        return '%s %s, %s, %s' %(self.first, self.last, self.gender, self.grade)

##    def __repr__(self):
##        return self.__str__()

class Course(object):

    def __init__(self, subject, teacher, period, for_grades):
        self.teacher = teacher
        self.period = int(period)
        self.subject = subject
        self.for_grades = map(int, for_grades)
        self.teacher.add_course(self)
        self.students = []
        self.boys = 0
        self.girls = 0
        self.update()

    def get_teacher(self):
        return self.teacher

    def get_period(self):
        return self.period

    def get_subject(self):
        return self.subject

    def get_students(self):
        return self.students

    def add_student(self, student):
        self.students.append(student)
        self.update()

    def count(self):
        return len(self.students)

    def is_subject(self, subject):
        if subject == self.subject: return True
        if subject == MATH and self.subject in MATH_COURSES: return True
        return False

    def is_math(self):
        return self.is_subject(MATH)

    def rem_student(self, student):
        if student in self.get_students():
            self.students.remove(student)
            #print student.first,student.last,'removed from',self
        self.update()

    def update(self):
        boys = 0
        girls = 0
        for i in self.students:
            if i.gender == BOY:
                boys += 1
            else:
                girls += 1
        self.boys = boys
        self.girls = girls

    def get_course_name(self):
        grades = ''
        for i in self.for_grades:
            if len(grades)>0: grades += '/'
            grades += str(i)
        return 'p%s %s %s %s' % (self.period, grades, self.subject, self.teacher.last)

    def __str__(self):
        return self.get_course_name()

##    def __repr__(self):
##        return self.__str__()

class Teacher(object):

    def __init__(self, last, subject,first='', schedule = {}):
        self.first = first
        self.last = last
        assert subject in SUBJECTS, subject +' not in ' +str(SUBJECTS)+', choose a valid subject.'
        self.subject = subject
        self.schedule = {}

    def add_course(self, course):
        self.schedule[int(course.period)] = course

    def get_last(self):
        return self.last

    def get_first(self):
        return self.first

    def get_subject(self):
        return self.subject

    def get_schedule(self):
        return self.schedule

    def __str__(self):
        return '%s %s' % (self.first, self.last)

##    def __repr__(self):
##        return self.__str__()
