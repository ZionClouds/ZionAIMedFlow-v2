import { createEffect, createSignal, For } from 'solid-js'
import axios from 'axios'
import { TbPlayerRecordFilled } from 'solid-icons/tb'
import { FiSearch, FiUpload } from 'solid-icons/fi'
import Popup from './components/popup'
import { IoExpand } from 'solid-icons/io'
import { AiOutlineEdit } from 'solid-icons/ai'

const BASE_URL = import.meta.env.VITE_BASE_URL as string

export interface INote {
  pid: string
  id: string
  status: string
  file_id: string
  file_url: string
  transcription: string
  notes: string
  updatedNotes: string
  updated: Date
}

function App() {
  const [authorized] = createSignal(true)
  const [user] = createSignal({ name: 'Jane Marie Doe, MD', id: 'jmdoe', email: 'jmdoe@mdpartners.com' })
  const [file, setFile] = createSignal<File | null>(null)
  const [uploading, setUploading] = createSignal(false)
  const [notes, setNotes] = createSignal<INote[]>([])
  const [showmodal, setShowModal] = createSignal(false)
  const [selectedNote, setSelectedNote] = createSignal<INote | null>(null)
  const [selectedTarget, setSelectedTarget] = createSignal('transcription')

  const uploadFile = async (file: File) => {
    if (uploading())
      return

    if (!file) {
      alert('No file was selected for upload')
      return
    }

    setUploading(true)
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(BASE_URL + 'upload/' + user().id, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('File uploaded successfully:', response.data);
    } catch (error) {
      console.error('Error uploading file:', error);
    }
    finally {
      setFile(null)
      setUploading(false)
    }
  }

  const handleFileChange = (event: Event) => {

    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      //alert('File changed')
      setFile(file)
    }
  }

  const handleUpload = async () => {
    if (file()) {
      await uploadFile(file()!)
    }
  }

  const updateNotes = async () => {
    try {
      const response = await axios.get<INote[]>(BASE_URL + 'notes/' + user().id);
      const data = response.data;
      setNotes(data)
      console.log('Notes updated:', response.data);
    } catch (error) {
      console.error('Error updating notes:', error);
    }
  }

  createEffect(() => {
    const interval = setInterval(async () => {
      await updateNotes();
    }, 2000);

    return () => clearInterval(interval);
  });

  const edit = async (note: INote) => {
    try {
      await axios.post(BASE_URL + 'notes', note);
    }
    catch (error) {
      console.error('Error updating notes:', error);
    }
    finally {
      setShowModal(false)
    }
  }

  return (
    <>
      <header class="h-[45px] flex items-center bg-slate-950 text-white px-3">
        <div class="flex-grow">
          <h1 class="font-bold text-lg">My MD Notes</h1>
        </div>
        <div class='space-x-2'>
          {authorized() && <>
            <span class='text-sm bg-slate-800 p-1'>Jane Marie Doe, MD</span>
            <button>Logout</button>
          </>}
          {!authorized() && <>
            <button>Login</button>
          </>}
        </div>
      </header>

      <section class="h-[calc(100vh-45px-30px)] overflow-auto flex flex-col bg-slate-900 text-white">
        <section class="flex items-center">
          <button class="w-[75px] h-[75px] md:w-[125px] md:h-[125px] bg-red-600 text-white font-semibold flex flex-col items-center justify-center">
            <TbPlayerRecordFilled class='text-2xl md:text-5xl' />
            <span>Record Audio</span>
          </button>

          <div class='w-[75px] h-[75px] md:w-[125px] md:h-[125px] bg-blue-600 text-white font-semibold flex flex-col items-center justify-center'>
            <label for="file-upload" class='hover:bg-blue-700 hover:cursor-pointer p-1 text-sm'>
              Upload
            </label>
            <div class="w-full overflow-clip">
              <div class="truncate text-xs text-white px-1">
                {file() ? <label title={file()?.name}>{file()?.name}</label> : <span>&nbsp;</span>}
              </div>
            </div>
            <input class="text-sm hidden"
              type="file" id="file-upload" onChange={handleFileChange} />
            <button class='bg-blue-600 px-1 hover:bg-blue-700' onClick={handleUpload}>
              <FiUpload class={'text-xl md:text-3xl ' + (uploading() ? "animate-pulse" : "")} />
            </button>
          </div>
        </section>
        <section class="h-full bg-slate-800 p-4">
          <h2 class='mb-4 text-lg font-bold text-center'>Processed Encounters</h2>
          <div class='flex mb-2 items-center'>
            <div class="flex-grow"></div>
            <input type="search" class='w-full md:max-w-[300px] outline-none resize-none border text-black' />
            <FiSearch />
          </div>
          <For each={notes()}>
            {note => <div class='flex flex-col mb-4 bg-gray-600 rounded-lg overflow-clip shadow-lg text-sm md:text-base'>
              <div class='hidden md:flex bg-black text-white space-x-1 md:space-x-2 items-center'>
                <label class='font-semibold p-2 uppercase'>File ID</label>
                <label class='p-2'>{note.file_id}</label>

                <label class='font-semibold p-2'>Date</label>
                <label class='p-2'>{(new Date(note.updated)).toLocaleString()}</label>

                <div class="flex-grow"></div>
                <label class='font-semibold p-2 uppercase'>Status</label>
                <label class='bg-green-700 p-2'>{note.status}</label>
              </div>
              <div class='flex flex-col md:hidden px-2 mt-2 bg-black'>
                <div class='flex space-x-2'>
                  <label class='font-semibold uppercase w-12'>File ID</label>
                  <label class=''>{note.file_id}</label>
                  <div class="flex-grow"></div>
                  <label class='font-semibold uppercase'>Status</label>
                  <label class='bg-green-700'>{note.status}</label>
                </div>
                <div class='flex items-center space-x-2'>
                  <label class='font-semibold uppercase w-12'>Date</label>
                  <label class=''>{(new Date(note.updated)).toLocaleString()}</label>
                </div>
              </div>

              <div class='flex px-2 items-center mt-2'>
                <label class='font-semibold uppercase'>Transcript</label>
                <button class='px-3' title='expand'
                  onClick={() => { setSelectedNote(note); setSelectedTarget('transcription'); setShowModal(true) }}
                ><IoExpand /></button>
                <div class="flex-grow"></div>
              </div>
              <div class='p-2'>
                <textarea rows={4} class='w-full border outline-none resize-none p-1 bg-gray-700' value={note.transcription} />
              </div>

              <div class='flex px-2 items-center mt-2'>
                <label class='font-semibold uppercase'>Notes</label>
                <button class='px-3' title='expand'
                  onClick={() => { setSelectedNote(note); setSelectedTarget('edit'); setShowModal(true) }}
                ><AiOutlineEdit /></button>
                <div class="flex-grow"></div>
              </div>
              <div class='p-2'>
                <textarea rows={4} class='w-full border outline-none resize-none p-1 bg-gray-700' value={note.updatedNotes} />
              </div>

            </div>}
          </For>
        </section>
      </section>

      {showmodal() &&
        <Popup note={selectedNote()} target={selectedTarget()} closeModal={() => setShowModal(false)} edit={edit} />
      }

      <footer class="bg-slate-900 h-[30px] text-slate-100 flex items-center text-xs px-2">
        <span>Ver: 0.0.1a</span>
      </footer>
    </>
  )
}

export default App
