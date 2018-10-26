# Documentation
### TABLE OF CONTENT
[Class User](#1-public-class-user)

    

[Class Student](#2-public-class-student)

     

[Class Quiz](#3-public-class-quiz)

    

[Class Quizscore](#4-public-class-quizscore)

     

[Class Words](#5-public-class-words)


#1. public class User

    
    The Class User used to login/ signup Student and if login user can
    add/remove his quiz and can give quiz and can see quiz score

#### `static Student student=null`
    
The login student object of Student class

#### `static ArrayList<Quiz>quiz=new ArrayList<>()`

The Quiz object array contains all the quiz from all students

#### `static ArrayList<Student>students=new ArrayList<>()`

The array of object of Student class

### `static boolean loginStudent(String username)`

Login student method used to login the student

 * **Parameters:** `username` — unique username of a student to login  * **Returns:** true, if successful

### `static boolean addStudent(String username, String major, String senioritylevel, String eamiladdress)`

Adds the student.

 * **Parameters:**    * `username` — the username    * `major` — the major    * `senioritylevel` — the seniority level    * `eamiladdress` — the eamil address of student  * **Returns:** true, if successful


### `void addQuiz(String quizname, String description, ArrayList<Words> word, ArrayList<Words> incorrectword)`

Adds new quiz in quiz array of object

 * **Parameters:**    * `quizname` — the quiz unique name    * `description` — the short description    * `word` — the word is a array of word obect containing N elements provided by user    * `incorrectword` — the  array of incorrectword obect containing N*3 elements provided by user

### `void removeQuiz(int quizindex)`

Removes the quiz object from array of Quiz

 * **Parameters:** `quizindex` — the quiz array index from which the quiz to delete

### `void giveQuiz(int quizindex)`

This method create a random N number of questions having 3 wrong option and 1 correct from selected quiz by user after competition of quiz score is saved to the quiz object

 * **Parameters:** `quizindex` — the quiz index

### `void showScore(int Studentname)`

Show score of a student

 **Parameters:** `Studentname` — the student name unique name of student is passed to see her score
 

# 2.public class Student
  
	The Class Student.

#### `String username`

The username.

#### `String major`

The major.

#### `String senioritylevel`

The seniority level.

#### `String email address`

The email address.

#### `static ArrayList<Quizscore>quizscore=new ArrayList<>()`

The quiz score.

### `public Student(String username, String major, String senioritylevel, String eamiladdress)`

Instantiates a new student.

 * **Parameters:**    * `username` — the username    * `major` — the major    * `senioritylevel` — the seniority level    * `eamiladdress` — the email address

### `public String getUsername()`

Gets the username.

 * **Returns:** the username

### `public void setUsername(String username)`

Sets the username.

 * **Parameters:** `username` — the new username

### `public String getMajor()`

Gets the major.

 * **Returns:** the major

### `public void setMajor(String major)`

Sets the major.

 * **Parameters:** `major` — the new major

### `public String getSenioritylevel()`

Gets the seniority level.

 * **Returns:** the seniority level

### `public void setSenioritylevel(String senioritylevel)`

Sets the seniority level.

 * **Parameters:** `senioritylevel` — the new seniority level

### `public String getEmailaddress()`

Gets the email address.

 * **Returns:** the email address

### `public void setEmailaddress(String eamiladdress)`

Sets the email address.

 **Parameters:** `eamiladdress` — the new email address.
 

# 3.public class Quiz


    
    The Class Quiz.

#### `String quizname`

The quiz name.

#### `String description`

The description.

#### `ArrayList<Words> word=new ArrayList<>(10)`

The word array of N Word object

####`ArrayList<Words> incorrectword=new ArrayList<>(30)`
The incorrect words array of N*3 Word object

#### `ArrayList<Quizscore> quizscore=new ArrayList<>(30)`

The array of Quiz score object

### `public Quiz(String quizname, String description, ArrayList<Words> word, ArrayList<Words> incorrectword)`

Instantiates a new quiz.

 * **Parameters:**    * `quizname` — the quiz name    * `description` — the description    * `word` — the word    * `incorrectword` — the incorrect word

### `void addQuizScore(String date,Double percentagescore)`

Adds the quiz score.

 * **Parameters:**    * `date` — the date    * `percentagescore` — the percentage score

### `Quizscore showRandomQuestion()`

Show random question.

  **Returns:** the quiz score
 

# 4.public class Quizscore


    
    The Class Quizscore.

#### `Student student`

The student object.

#### `String date`

The date.

#### `Double percentagescore`

The percentage score .

### `public Quizscore(String date, Double percentagescore)`

Instantiates a new quiz score.

 * **Parameters:**    * `date` — the date    * `percentagescore` — the percentage score


# 5.public class Words



The Class Words.

#### `String words`

The words.

#### `String definition`

The definition.

### `public Words(String words, String definition)`

Instantiates a new words.

 * **Parameters:**    * `words` — the words    * `definition` — the definition



