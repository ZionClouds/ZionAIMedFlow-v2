//import { createSignal } from 'solid-js'
// import solidLogo from './assets/solid.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

import { For } from "solid-js"

const pdfFilePath = "https://assets.ctfassets.net/l3l0sjr15nav/29D2yYGKlHNm0fB2YM1uW4/8e638080a0603252b1a50f35ae8762fd/Get_Started_With_Smallpdf.pdf"

const doc = [
  { "page": 1, "text": "Get Started With Smallpdf" },
  { "page": 2, "text": "Get Started With Smallpdf" },
]

function App() {
  // const [count, setCount] = createSignal(0)

  return (
    <>
      <header class="h-[45px] flex items-center bg-slate-950 text-white">
        <h1 class="text-lg font-bold ">PDF Approver</h1>
      </header>
      <div class="flex flex-row h-[calc(100vh-80px)]">
        <main class="basis-1/2 bg-yellow-100">
          {/* <PDFViewerComponent {...{ pdfFilePath }} /> */}
          <object data={pdfFilePath} type="application/pdf" class="h-[calc(100vh-90px)] w-full"></object>
        </main>
        <aside class="basis-1/4 bg-slate-800 text-white flex flex-col px-2 overflow-auto space-y-2">
          <label class="text-lg font-bold">Recognized Text</label>
          <For each={doc}>
            {item => (
              <>
                <span>Page: {item.page}</span>
                <textarea rows={5} class="bg-slate-700 min-h-[100px] outline-none resize-none  px-1 rounded">{item.text}</textarea>
              </>
            )}
          </For>
        </aside>
        <aside class="basis-1/4 flex flex-col px-2 bg-slate-800 text-white space-y-2 overflow-auto">
          <h2 class="text-lg font-bold">Review Information</h2>
          <label>Patient's name</label>
          <input type="text" class="text-black outline-none border px-1 rounded" />
          <label>Date of bith</label>
          <input type="text" placeholder="mm/dd/yyy" class="text-black outline-none border px-1 rounded w-36" />
          <label>Provider's name</label>
          <input type="text" class="text-black outline-none border px-1 rounded" />
          <label>Date of service</label>
          <input type="text" placeholder="mm/dd/yyy" class="text-black outline-none border px-1 rounded w-36" />
          <label>AI Notes</label>
          <label class="text-sm">Help me write it</label>
          <textarea rows={5} placeholder="notes" class="min-h-[100px] outline-none px-1 text-black resize-none rounded" />
          <div class="space-x-2">
            <button class="bg-blue-500 text-white rounded px-2 py-1">Approve</button>
            <button class="bg-red-500 text-white rounded px-2 py-1">Review</button>
          </div>
        </aside>
      </div>
      <footer class="flex flex-row items-center bg-slate-900 text-white h-[35px]">
        <span>Footer</span>
      </footer>
      {/* <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} class="logo" alt="Vite logo" />
        </a>
        <a href="https://solidjs.com" target="_blank">
          <img src={solidLogo} class="logo solid" alt="Solid logo" />
        </a>
      </div>
      <h1>Vite + Solid</h1>
      <div class="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count()}
        </button>
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p class="read-the-docs">
        Click on the Vite and Solid logos to learn more
      </p> */}
    </>
  )
}

export default App
