import mysql
import mysql.connector
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidgetItem, QHeaderView, QErrorMessage, QPushButton, QHBoxLayout, QMessageBox
from PyQt5 import uic, QtCore


#cursor for manipulating database
db = mysql.connector.connect(host = 'localhost', user = 'root', password = '*P@ssw0rd', database = 'sisv2')
mydb = db.cursor()


class CourseForm(QMainWindow):
    
    def __init__(self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/course.ui', self)
        self.course_done.pressed.connect(self.done_pressed)
        self.fields = [self.course_id,self.course_name]
        self.mode = ''
        self.selected_course = ''
    
    def done_pressed(self):
        if self.mode == 'Add':
            self.add_course()
        elif self.mode == 'Edit':
            self.edit_course()

    def clear_fields(self):
        for i in range(len(self.fields)):
            self.fields[i].clear()

    def add_course(self):
        courseId = self.course_id.text()
        courseName = self.course_name.text()
        course = [courseId, courseName]
        mydb.execute(f"INSERT INTO courses VALUES('{course[0]}','{course[1]}')")
        db.commit()
        self.close() 
        my_app.show_courses()
        self.clear_fields() 

    def fill_course(self):
        mydb.execute(f"SELECT * from courses where courseId = '{self.selected_course}'")
        rows = mydb.fetchone()
        self.course_id.setText(rows[0])
        self.course_name.setText(rows[1])
    
    def edit_course(self):
        courseId = self.course_id.text()
        courseName = self.course_name.text()
        course = [courseId, courseName]
        mydb.execute(f"UPDATE courses SET courseId = '{course[0]}', courseName = '{course[1]}'  WHERE courseId = '{self.selected_course}'")
        db.commit()
        my_app.show_courses()
        self.close()

class StudentForm(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.mode = ''
        self.selected_id = ''
        uic.loadUi(f'{sys.path[0]}/form.ui', self)
        self.student_done.pressed.connect(self.done_pressed)
        self.fields = [self.id_number,self.full_name,self.gender,self.course_code,self.year_level]
        self.coursescombo = []
        self.gendercombo = ['Male', 'Female']
        self.yearcombo = ['1','2','3','4','5','6']

    def set_combos(self,courses):
        self.gender.addItems(self.gendercombo)
        self.year_level.addItems(self.yearcombo)
        self.coursescombo = courses
        self.course_code.addItems(self.coursescombo)
    
    def done_pressed(self):
        if self.mode == 'Add':
            self.add_student()
        elif self.mode == 'Edit':
            self.edit_student()

    
    def clear_fields(self):
        for i in range(len(self.fields)):
            if i >= 2:
                self.fields[i].setCurrentIndex(0)
                continue
            self.fields[i].clear()
            
    
    def add_student(self):
        idnumber = self.id_number.text()
        fullname = self.full_name.text()
        gender = self.gender.currentText()
        coursecode = self.course_code.currentText()
        year = int(self.year_level.currentText())
        student = [idnumber, fullname, year, gender, coursecode]
        mydb.execute(f"INSERT INTO STUDENT VALUES('{student[0]}','{student[1]}',{student[2]},'{student[3]}','{student[4]}')")
        db.commit()
        self.close() 
        my_app.show_students() 
        self.clear_fields() 


    def fill_student(self):
        mydb.execute(f"SELECT * from STUDENT where idNo = '{self.selected_id}'")
        rows = mydb.fetchone()
        self.id_number.setText(rows[0])
        self.full_name.setText(rows[1])
        self.year_level.setCurrentIndex(self.yearcombo.index(str(rows[2])))
        self.gender.setCurrentIndex(self.gendercombo.index(str(rows[3])))
        try:
            self.course_code.setCurrentIndex(self.coursescombo.index(str(rows[4])))
        except ValueError:
            self.course_code.setCurrentIndex(0)

    
    def edit_student(self):
        idnumber = self.id_number.text()
        fullname = self.full_name.text()
        gender = self.gender.currentText()
        coursecode = self.course_code.currentText()
        year = int(self.year_level.currentText())
        student = [idnumber, fullname, year, gender, coursecode]
        mydb.execute(f"UPDATE STUDENT SET fullName = '{student[1]}', idNo = '{student[0]}', yearLevel = '{student[2]}', gender = '{student[3]}', courseCode = '{student[4]}'  WHERE idNo = '{self.selected_id}'")
        db.commit()
        my_app.show_students()
        self.close()


class MainWindow(QMainWindow):


    def __init__(self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/main.ui', self)
        self.student_search.pressed.connect(self.search_student)     #student tab
        self.student_add.pressed.connect(lambda: self.open_form('Add'))
        self.student_edit.pressed.connect(lambda: self.open_form('Edit'))
        self.student_refresh.pressed.connect(self.show_students)
        self.student_table.itemClicked.connect(self.set_selected_id)
        self.student_delete.pressed.connect(self.delete_student)
        self.selected_id = ''

        self.course_search.pressed.connect(self.search_course)     #course tab
        self.course_add.pressed.connect(lambda: self.open_course('Add'))
        self.course_edit.pressed.connect(lambda: self.open_course('Edit'))
        self.course_refresh.pressed.connect(self.show_courses)
        self.course_table.itemClicked.connect(self.set_selected_course)
        self.course_delete.pressed.connect(self.delete_course)

        self.selected_course = ''

        self.pop_up = QErrorMessage()
        self.pop_up.setWindowTitle("Error")
        self.student_form_window = StudentForm() 
        self.course_form_window = CourseForm() 
        self.dropdowns = []
        self.show_students()
        self.show_courses()
        self.setComboBox()

    def search_student(self):
        find = self.student_searchbar.text()
        self.show_students(find)
    
    def search_course(self):
        find = self.course_searchbar.text()
        self.show_courses(find)

    def set_selected_course(self, item):
        self.selected_course = item.text()

    def set_selected_id(self, item):
        self.selected_id = item.text()
    
    def setComboBox(self):
        self.student_form_window.course_code.clear()
        self.dropdowns = []
        mydb.execute(f"SELECT courseId FROM courses ORDER BY courseId ASC")
        rows = mydb.fetchall()
        for item in rows:
            self.dropdowns.append(*item)
        self.student_form_window.set_combos(self.dropdowns)
        
    def delete_course(self):
        mydb.execute(f"DELETE FROM courses WHERE courseId = '{self.selected_course}'")
        db.commit()
        self.show_courses()

    def delete_student(self):
        mydb.execute(f"DELETE FROM student WHERE idNo = '{self.selected_id}'")
        db.commit()
        self.show_students()

    def open_form(self, mode = 'None'): 
        self.student_form_window.clear_fields()

        if mode == 'Edit': 
            self.student_form_window.show()
            self.student_form_window.mode = 'Edit'
            self.student_form_window.selected_id = self.selected_id
            self.student_form_window.fill_student()
            
        elif mode == 'Add':
            self.student_form_window.show()
            self.student_form_window.mode = 'Add'

    def open_course(self, mode = 'None'): 
        self.course_form_window.clear_fields()
        
        if mode == 'Edit': 
            self.course_form_window.show()
            self.course_form_window.mode = 'Edit'
            self.course_form_window.selected_course = self.selected_course
            self.course_form_window.fill_course()
            
        elif mode == 'Add':
            self.course_form_window.show()
            self.course_form_window.mode = 'Add'

    def show_courses(self, courseCode = None):
        self.setComboBox()
        hheader = self.course_table.horizontalHeader()         
        hheader.setSectionResizeMode(QHeaderView.Stretch)
        vheader = self.course_table.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.ResizeToContents)      
        numColumn = 2
        if courseCode == None:
            mydb.execute("SELECT courseId, courseName from courses")
        else:
            mydb.execute(f"SELECT courseId, courseName from courses where courseId = '{courseCode}'")
        rows = mydb.fetchall()
        numRows = len(rows)
        self.course_table.setColumnCount(numColumn)
        self.course_table.setRowCount(numRows)
        
        for i in range(numRows):
            for j in range(numColumn):
                self.course_table.setItem(i, j, QTableWidgetItem(str(rows[i][j])))


    def show_students(self, idNumber = None):
        self.setComboBox()
        hheader = self.student_table.horizontalHeader()         
        hheader.setSectionResizeMode(QHeaderView.Stretch)
        vheader = self.student_table.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.ResizeToContents)      
        numColumn = 6
        if idNumber == None:
            mydb.execute("SELECT idNo, fullName, yearLevel, gender, courseCode from student")
        else:
            mydb.execute(f"SELECT idNo, fullName, yearLevel, gender, courseCode from student where idNo = '{idNumber}'")

        rows = mydb.fetchall()
        numRows = len(rows)
        self.student_table.setColumnCount(numColumn)
        self.student_table.setRowCount(numRows)
        
        for i in range(numRows):
            for j in range(numColumn):
                try:
                    if j == 5:
                        mydb.execute(f"SELECT courseName from courses where courseId = '{rows[i][4]}'")
                        endcolumn = mydb.fetchone()
                        self.student_table.setItem(i, j, QTableWidgetItem(str(endcolumn[0])))
                        continue
                    self.student_table.setItem(i, j, QTableWidgetItem(str(rows[i][j])))
                except TypeError:
                    self.student_table.setItem(i, j, QTableWidgetItem('None'))
    

if __name__ == '__main__': 
    app = QApplication(sys.argv) 
    my_app = MainWindow() 
    my_app.show() 
    print(sys.argv) 

    try: 
        sys.exit(app.exec_()) 
    except (SystemExit): 
        print("Closing window...") 
