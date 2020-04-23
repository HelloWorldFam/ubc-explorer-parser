const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');

// server settings - make sure that your port doesn't conflict with the React port!
const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// MongoDB configuration
const uri = 'mongodb+srv://HelloWorld:helloworld123@bcsexplorer-rahrv.gcp.mongodb.net/test?retryWrites=true&w=majority';
mongoose.connect(uri, { useUnifiedTopology: true, useNewUrlParser: true, useCreateIndex: true });

const connection = mongoose.connection;
connection.once('open', () => {
  console.log("MongoDB database connection established successfully");
})

// code: the course code, like CPSC 121
// name: the course name, like Models of Computation
// desc: the course description, like Functions, derivatives, optimization...
// prer: the raw course prerequisites, like Either (a) CPSC 221 or (b) ...
// crer: the raw course corequisites, like All of CPSC 213, CPSC 221.
// preq: the parsed course prerequisites, like CPSC 221 or (CPSC 260 and ...
// creq: the parsed course corequisites, like `CPSC 213 and CPSC 221
// excl: the courses that cannot be taken for credit after the course is taken, in a comma-separated list, like STAT 200, STAT 203, BIOL 300, COMM 291, ...
// term: the terms in which the course is offered, like 2017S, 2017W
// cred: the number of credits granted by the course, like 3, or even a comma-separated list for courses with variable credits, like 3, 6

const { Schema } = mongoose;
const CoursesSchema = new Schema({
  code: String,
  name: String,
  desc: String,
  prer: String,
  preq: String,
  crer: String,
  creq: String,
  excl: String,
  term: String,
  cred: String
});
const Courses = mongoose.model('Courses', CoursesSchema);

app.get('/', (req, res) => {
  Courses.find()
    .then(courses => res.json(courses))
    .catch(err => res.status(400).json(`Error ${err}`))
});

app.post('/add', (req, res) => {
  const body = req.body;
  const course = new Courses(body);
  console.log(course);
  course.save(body)
    .then(course => {
      res.json(course);
      console.log('Course saved successfully.');
    })
    .catch(err => console.log(`Error ${err}`));
});

app.listen(port, () => {
  console.log(`Server is running on port: ${port}`);
});