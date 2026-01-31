import axios from 'axios';
import cors from 'cors';
import 'dotenv/config';
import express from 'express';

const app = express();
const PORT = process.env.PORT;
const BASE_URL = process.env.PY_BASE_URL;

app.use(express.json())
app.use(cors())

app.get('/hello', async(req, res) =>{
    try {
        const py_res = await axios.get(BASE_URL);
        res.send(py_res.data)
    } catch (error) {
        console.log('server error', error)
        res.send('server error')
    }
});

app.get('/response', async(req, res) =>{
    try {
        const py_res = await axios.post(`${BASE_URL}/generate`, {
            question: "Is water dangerous?"
        });   
        res.send(py_res.data)
    } catch (error) {
        console.log('server error', error)
        res.send('server error')
    }
});

app.listen(4000, ()=>{
    console.log('server started')
})