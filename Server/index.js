import axios from "axios";
import cors from "cors";
import "dotenv/config";
import express from "express";

const app = express();
const PORT = process.env.PORT;
const BASE_URL = process.env.PY_BASE_URL;

app.use(express.json());
app.use(cors());

app.get("/hello", async (req, res) => {
  try {
    const py_res = await axios.get(BASE_URL);
    res.send(py_res.data);
  } catch (error) {
    console.log("server error", error);
    res.send("server error");
  }
});

app.get("/response", async (req, res) => {
  try {
    const py_res = await axios.post(`${BASE_URL}/generate`, {
      question: "Is water dangerous? in simple one sentence",
    });
    res.send(py_res.data);
  } catch (error) {
    console.log("server error", error);
    res.send("server error");
  }
});
app.get("/stream", async (req, res) => {
  try {
    const py_res = await axios.post(
      `${BASE_URL}/stream`,
      { question: "Is water dangerous? in simple one sentence" },
      { responseType: "stream" },
    );
    res.setHeader("Content-type", "text/plain");

    const stream = py_res.data;
    stream.on("data", (chunk) => {
      res.write(chunk);
    });

    stream.on("end", () => {
      res.end();
    });

    stream.on("error", (err) => {
      console.log("stream error", err);
      res.end();
    });
  } catch (error) {
    console.log("server error", error);
    res.send("server error");
  }
});

app.get("/system_prompt", async (req, res) => {
  try {
    const py_res = await axios.post(
      `${BASE_URL}/system`,
      { question: "Is water dangerous? in simple one sentence" }
    );

    console.log(py_res.data)
    res.send(py_res.data)
  } catch (error) {
    console.log("server error", error);
    res.send("server error");
  }
});

app.get("/tool", async (req, res) => {
  try {
    const py_res = await axios.post(
      `${BASE_URL}/tool`,
      { question: "what is the current time" }
    );

    res.send(py_res.data)
  } catch (error) {
    console.log("server error", error);
    res.send("server error");
  }
});

app.get("/query", async (req, res) => {
  try {
    const py_res = await axios.post(
      `${BASE_URL}/db_tool`,
      { question: "what is my orders" }
    );

    res.send(py_res.data)
  } catch (error) {
    console.log("server error", error);
    res.send("server error");
  }
});

app.get('/insert_order', async(req, res) => {
  try {
    // const { amount, title } = req.body;

    // if(!amount || !title){
    //   return res.send("Enter body")
    // }

    const sendData = await axios.post(`${BASE_URL}/insert`,{
      userId: "u100",
      title: "Bike",
      status: "success",
      amount: 500000
    });

    res.send(sendData.data)
  } catch (error) {
    console.log("server error", error);
    res.send("server error");
  }
});

app.get('/memory', async(req, res) => {
  try {
    const response = await axios.post(`${BASE_URL}/memory_model`, {
      userId: "u100",
      question: "what is water explain in simple one line sentence"
    });

    if(!response){
      return res.send("Not found")
    }

    res.send(response.data)
  } catch (error) {
    console.log("server error", error);
    res.send("server error");
  }
})

app.get('/test', async(req, res) =>{
  try {
    const response = await axios.post(`${BASE_URL}/rapid`,{
      userId: "u100",
      question: "what is the last question ? in one sentence"
    });

    if(!response){
      return res.send("Not found")
    }

    res.send(response.data)
  } catch (error) {
    console.log("server error", error);
    res.send("server error");
  }
})

app.listen(4000, () => {
  console.log("server started");
});
