import { createEffect, createSignal, For } from 'solid-js'
import axios from 'axios'
import { TbPlayerRecordFilled } from 'solid-icons/tb'
import { FiSearch, FiUpload } from 'solid-icons/fi'
import Popup from './components/popup'
import { IoExpand } from 'solid-icons/io'
import { AiOutlineEdit } from 'solid-icons/ai'

// @ts-ignore
const BASE_URL = window.base_url;
//const BASE_URL = import.meta.env.VITE_BASE_URL as string

export async function GetAuthHeader() {
  function IsExpired(token_expiration_date: string) {
    var date = new Date(token_expiration_date).getTime();
    var now = new Date().getTime();
    var diffInMS = now - date;
    var msInHour = Math.floor(diffInMS / 1000 / 60);
    if (msInHour < 55) {
      //console.log('Within hour');
      return false;
    } else {
      //console.log('Not within the hour');
      return true
    }
  }
  function GetTokenExpirationDate(token: string) {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map(function (c) {
          return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
        })
        .join("")
    );

    const { exp } = JSON.parse(jsonPayload);
    //const expired = Date.now() >= exp * 1000
    const expired = exp * 1000
    return expired
  }

  try {
    const respEasyAuthToken = await axios.get(".auth/me")
    //const currentTokenExpirationDate = respEasyAuthToken.data[0].expires_on
    const current_id_token = respEasyAuthToken.data[0].id_token
    const currentTokenExpirationDate = GetTokenExpirationDate(current_id_token)
    console.log("Checking if id_token is expired")
    console.log("Current Token Expiration Date: ", currentTokenExpirationDate)
    if (IsExpired(currentTokenExpirationDate.toString())) {
      console.log("Token is expired, refreshing token at .auth/refresh")
      const refreshEasyAuthToken = await axios.get(".auth/refresh")
      if (refreshEasyAuthToken.status === 200) {
        console.log("Token refreshed successfully")
        var renewedToken
        do {
          renewedToken = await axios.get(".auth/me")
          var id_token = renewedToken.data[0].id_token
          var headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + id_token
          }
          return headers
        }
        while (IsExpired(renewedToken.data[0].expires_on))

      } else {
        console.log("Token refresh failed")
      }
    } else {
      console.log("Token is not expired")
      var id_token = respEasyAuthToken.data[0].id_token
      var headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + id_token
      }
      return headers
    }
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error
  }
}

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
  //const [authorized] = createSignal(true)
  const [user] = createSignal({ name: 'Jane Marie Doe, MD', id: 'jmdoe', email: 'jmdoe@mdpartners.com' })
  const [file, setFile] = createSignal<File | null>(null)
  const [uploading, setUploading] = createSignal(false)
  const [notes, setNotes] = createSignal<INote[]>([])
  const [showmodal, setShowModal] = createSignal(false)
  const [selectedNote, setSelectedNote] = createSignal<INote | null>(null)
  const [selectedTarget, setSelectedTarget] = createSignal('transcription')
  const [readTokenName, setEasyAuthTokenUser] = createSignal<string>();
  //const [readEasyAuthTokenUserRole, setEasyAuthTokenUserRole] = createSignal<string[]>([]);

  const handleLogOut = (): void => {
    // Redirect to logout url
    const ask = confirm('Are you sure you want to logout?')
    if (ask)
      window.location.href = '.auth/logout'
  }

  // Loading Easy Auth Current Logged User and User Roles claims
  createEffect(async () => {
    try {
      const respEasyAuthToken = await axios.get(".auth/me")
      for (let tokenIndex = 0; tokenIndex < respEasyAuthToken.data.length; tokenIndex++) {
        const authToken = respEasyAuthToken.data[tokenIndex];
        for (let claimIndex = 0; claimIndex < authToken?.user_claims?.length; claimIndex++) {
          const claim = authToken.user_claims[claimIndex];
          if (claim.typ === 'name') {
            console.log('Name: ', claim.val)
            const newValue = claim.val
            setEasyAuthTokenUser(newValue)
            break
          }
        }
        // try {
        //   const token = JSON.parse(atob(authToken.id_token.split('.')[1]))
        //   setEasyAuthTokenUserRole(token.roles)
        // } catch (error) {
        //   console.log(error)
        //   setEasyAuthTokenUserRole([])
        // }
      }
    } catch (error) {
      console.log(error)
      setEasyAuthTokenUser("Unknown")
      //setEasyAuthTokenUserRole([])
    }
  })

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
      let headers = await GetAuthHeader()
      if (headers) {
        headers['Content-Type'] = 'multipart/form-data';
      }
      const response = await axios.post(BASE_URL + 'upload/' + user().id, formData, { headers });
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
      let headers = await GetAuthHeader()
      const response = await axios.get<INote[]>(BASE_URL + 'notes/' + user().id, { headers });
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
      let headers = await GetAuthHeader()
      await axios.post(BASE_URL + 'notes', note, { headers });
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
          {/* {authorized() && <>
            <span class='text-sm bg-slate-800 p-1'>Jane Marie Doe, MD</span>
            <button>Logout</button>
          </>}
          {!authorized() && <>
            <button>Login</button>
          </>} */}
          {(!!readTokenName()) && (
            <span class='text-sm bg-slate-800 p-1'>{readTokenName()}</span>
          )}
          <button class='button button-text font-semibold hover:underline' onclick={handleLogOut}>Sign&nbsp;out</button>
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
