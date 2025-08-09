import React, {useState} from 'react'
import axios from 'axios'

export default function Home(){
  const [title, setTitle] = useState('')
  const [project, setProject] = useState(null)
  const [status, setStatus] = useState(null)

  const start = async ()=>{
    const res = await axios.post('/api/projects', { title, max_papers: 7000 })
    setProject(res.data)
    pollStatus(res.data.project_id)
  }

  const pollStatus = async (id)=>{
    const iv = setInterval(async ()=>{
      const s = await axios.get(`/api/projects/${id}/status`)
      setStatus(s.data)
      if(s.data.status === 'done') clearInterval(iv)
    }, 1500)
  }

  return (
    <div style={{fontFamily:'Inter, sans-serif', padding:24}}>
      <h1 style={{fontSize:24, marginBottom:12}}>LitHybrid — Flat Frontend</h1>
      <input value={title} onChange={e=>setTitle(e.target.value)} placeholder="Enter title..." style={{width:'60%',padding:8}} />
      <button onClick={start} style={{marginLeft:8,padding:'8px 12px'}}>Start</button>

      {project && (
        <div style={{marginTop:20}}>
          <strong>Project:</strong> {project.project_id}
          <div style={{marginTop:8}}>
            <strong>Status:</strong> {status ? status.status : 'starting...'}
            <pre>{status ? JSON.stringify(status,null,2) : ''}</pre>
          </div>
        </div>
      )}
    </div>
  )
}
