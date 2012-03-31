from scheduler_classes import *
import os, re, random, copy, time

#EXPECTS A CSV FILE formatted
#last, first, gender, grade, homeroom, math_level

def schedule(schedule_grades=[]):
    pass
            
def get_students(from_grades=[]):
    """
    returns a list of all students, unless from_grades is a list containing values.
    In which case the function only returns students from the listed grades.
    """
    students = []

    f = open('student_placement.csv')
    c = 0
    for line in f:
        #print line
        c += 1
        #TODO: don't parse line 1...
        if (not re.match(',,,',line) or line in os.linesep) and not c == 1:
            a = line.split(DELIMITER) #OO Calc uses ";" instead of "," in csv... ugh!
            #print a
            last = a[0]
            first = a[1]
            gender = a[2]
            grade = int(a[3])
            homeroom = a[4]
            math_level=''
            if len(a)>5: math_level=a[5].rstrip()
            if not math_level in MATH_COURSES:
                print 'Error importing student data for:',first,last
                print 'Math level:',math_level,'does not match',MATH_COURSES
                raise Exception
            s = Student(first, last, gender, grade, homeroom, math_level)
            if grade in from_grades or len(from_grades)==0:
                students.append(s)
    return students

def get_teachers():
    tl = []
    global TEACHERS
    for i in TEACHERS:
        tl.append(Teacher(i[0],i[2],i[1]))
    return tl

def get_teacher(last):
    teachers = get_teachers()
    for i in teachers:
        if i.get_last().lower()==last: return i

def parse_course_text(text, subject=None):
    """
    "7" will be parsed as the grade level
    "Algebra (5 + 6)" will be parsed as Algebra, for 5th and 6th
    """
    p = re.compile(r'(?P<gr>\A\d+\Z)')
    res = re.match(p, text)
    if res:
        a = res.groupdict()
##        print 'Grade level course'
        return subject,  a['gr']
    else:
        q = re.compile(r'(?P<course>[a-zA-Z\-\s]+)\s*\(*(?P<gr>[0-9\+]+)\)*') #(?P<gr>[0-9\+])')
        res = re.match(q, text)
        assert res,text+' is not a valid course name. Must either be a digit or "course (grade + grade...)"'
        grades = []
        a = res.groupdict()
        r = re.compile(r'[0-9]+')
        for i in re.finditer(r,a['gr']):
            grades.append(int(i.group(0)))
        course = a['course'].rstrip()
        return course, grades
    return Exception(text+' not valid course')
            
def get_courses():
    """
    Returns a list of teachers and courses
    """
    courses = []
    teachers = get_teachers()
    t_by_col = {}
    f = open('teacher_schedules.csv')
    l = f.readlines()
    first_line = l[0].split(',')
    for i in range(len(first_line)):
        last = re.match('\w+',first_line[i]).group(0)
        t_by_col[i] = get_teacher(last)  
    for i in range(1,len(l)): #iterate through the file.
        line = l[i].split(',')
        period = line[0]
        for j in range(1,len(line)):
            t = t_by_col[j]
            try:
                subject, for_grades = parse_course_text(line[j],t_by_col[j].subject)
                if not t or subject in ['elective','prep']: raise Exception
            except:
                pass
            else:
                courses.append(Course(subject,t,period,for_grades))
    f.close()
    return courses

def get_grade_courses(for_grades=[],courses=[]):
    match = []
    for i in courses:
        add = False
        for j in for_grades:
            if j in i.for_grades: add = True
        if add: match.append(i)
    return match

def get_courses_sub(subject, courses=[]):
    if not courses: courses = get_courses() #default search all courses.
    match = []
    for i in courses:
        if i.is_subject(subject): match.append(i)
    return match

def schedule_one(s, courses = [], startwith=[]):
    for i in startwith: s.add_course(i)
    if not courses: courses = get_courses()
    my_c = s.get_valid_courses(courses)
    for j in SUBJECTS:
        o = s.get_subject_courses(j,my_c)
        opt = copy.copy(o)
        while j not in s.subjects_enrolled:
            if not opt:
                s.clear_schedule()
                startwith = [random.choice(o)]
                return schedule_one(s, courses, startwith)
            choice = random.choice(opt)
            s.add_course(choice)
            opt.remove(choice)
    return s

def schedule_one_v2(s, courses = [], startwith=[]):
    for i in startwith: s.add_course(i)
    if not courses: courses = get_courses()
    my_c = s.get_valid_courses(courses)
    for j in SUBJECTS:
        o = s.get_subject_courses(j,my_c)
        opt = copy.copy(o)
        while j not in s.subjects_enrolled:
            if not opt:
                s.clear_schedule()
                """
                [TODO]
                There is a bug on the next line... for Brian Gentry
                o is Null so random.choice(o) throws exception...
                """
                try:
                    startwith = [random.choice(o)]
                except:
                    print 'Exception!',s.first,s.last,s.math_level,j
                    print s.schedule
                    print s.subjects_enrolled
                    print 'my_c:'
                    for m in my_c: print m
                    print 'o:',o
                    print 'opt:',opt
                    
                return schedule_one_v2(s, courses, startwith)
            if random.choice([True, False]):
                choice = random.choice(opt)
            else:
                choice = min(opt, key=lambda opt:opt.count())
            s.add_course(choice)
            opt.remove(choice)
    return s

#Hard-coded to work for this years schedule
def write_schedule(s, c, fname=''):
    if not fname: fname = 'schedule-version-'+str(time.time())
    f = open(fname+'-s'+'.csv','w')
    f.write('%s, %s, %s, %s, %s, %s, %s, %s, %s\n' % ('first','last','grade','gender','p1','p2','p3','p5','p6'))
    for i in s:
        f.write('%s, %s, %s, %s, %s, %sNes, Mishri, Isabel, %s, %s, %s\n' % (i.first, i.last, i.grade, i.gender, i.schedule[1].teacher.last, i.schedule[2].teacher.last, i.schedule[3].teacher.last, i.schedule[5].teacher.last, i.schedule[6].teacher.last))

    f.close()
    f = open(fname+'-c'+'.csv','w')
    for i in c:
        f.write('Per %s, %s, b: %s, g: %s, t: %s\n' % (i.period, i.teacher.last, i.boys, i.girls, i.count()))
        f.write('first, last, full, grade, gender\n')      
        for j in i.students:
            f.write('%s, %s, %s, %s, %s\n' % (j.first, j.last, j.first+' '+j.last, j.grade, j.gender))
        f.write('\n\n')
    f.close()
    print 'Schedule saved to',fname

def schedule(s=[], c=[]):
    if not s: s = get_students([7,8])
    if not c: c = get_courses()
    c = sorted(c, key=lambda c:(c.teacher, c.period))
    print 'scheduling!!!'
    attempts = 0
    min_size = len(s)
    goOn = True
    fname = 'schedule-v-'+str(time.time())
    while goOn:
        #print 'attempt:',attempts
        for i in s:
            schedule_one_v2(i, c)
        max_size = 0
        for i in c:
            max_size = max(max_size, i.count())

        if min(max_size, min_size) < min_size:
            #a better find!
            print 'Best schedule yet, min size:',min_size
            write_schedule(s, c, fname)
            min_size = max_size
        #print 'Largest class at:',max_size
        if max_size < 30: goOn = False
        
        else:
            for i in s:
                i.clear_schedule()
            attempts += 1
        if attempts % 1000 == 0: print attempts,'attempts and counting.'
    print 'see "s" and "c" for students and courses...'
    print 'schedule took',attempts,'attempts to generate.'



