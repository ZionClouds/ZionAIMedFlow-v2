import { FiUpload } from "solid-icons/fi"
import { Component, createSignal } from "solid-js"
import { INote } from "../../../interfaces";
import Notes from "../Notes";


interface MainProps {
  file: File | null;
  isUploading: boolean;
  notes: INote[]
  modalNote: INote | null
  modalTarget: string
  showmodal: boolean
  onFileChange: (event: Event) => void
  onUpload: () => void
  onCloseModal: () => void
  onOpenModal: () => void
  modalEdit: (note: INote) => void
  onSelectNote: (note: INote) => void
  onSelectTarget: (type: string) => void
}

const Main: Component<MainProps> = (props) => {
  const [isNote, setIsNote] = createSignal<boolean>(false)

  const handleNoteClick = () => {
    setIsNote(!isNote())
  }

  return (
    <div class="relative w-[100vw] h-[calc(100vh-65px)] z-0">
      <img class="absolute top-0 left-0 w-full h-full object-cover opacity-10" src="/src/assets/images/backgrounds/zionai-bg.png" alt="zionai" />
      <div class="flex items-center justify-center w-full h-full relative z-50">
        <div class="w-full">
          {!isNote() ? (
            <div>
              <svg class="mb-6 block mx-auto" xmlns="http://www.w3.org/2000/svg" width="13em" height="13em" viewBox="0 0 24 24">
                <defs>
                  <linearGradient id="grad1" x1="0%" x2="100%" y1="0%" y2="0%">
                    <stop offset="0%" stop-color="#3D5BA9" />
                    <stop offset="100%" stop-color="#A6D49A" />
                  </linearGradient>
                </defs>
                <g fill="url(#grad1)">
                  <path d="M8.25 4.5a3.75 3.75 0 1 1 7.5 0v8.25a3.75 3.75 0 1 1-7.5 0z"></path>
                  <path d="M6 10.5a.75.75 0 0 1 .75.75v1.5a5.25 5.25 0 1 0 10.5 0v-1.5a.75.75 0 0 1 1.5 0v1.5a6.75 6.75 0 0 1-6 6.709v2.291h3a.75.75 0 0 1 0 1.5h-7.5a.75.75 0 0 1 0-1.5h3v-2.291a6.75 6.75 0 0 1-6-6.709v-1.5A.75.75 0 0 1 6 10.5"></path>
                </g>
              </svg>

              {/* Voice record button 
              <button class="button button-green !text-xl mb-6 block mx-auto">Automated Note Taking</button>*/}

              {/* Media file upload button */}
             {/*} <label for="file-upload"
                class="button button-text mx-auto flex items-center justify-center"
              >
                <FiUpload class={'text-xl mr-2' + (props.isUploading ? "animate-pulse" : "")} /> Upload an audio file
              </label>*/}
            {/* Media file upload button */}
            <label
            for="file-upload"
              class="button button-green block flex items-center justify-center mx-auto w-fit px-4 py-2"
          >
            <FiUpload class={'text-xl mr-2' + (props.isUploading ? " animate-pulse" : "")} />
              {props.isUploading ? "Uploading..." : "Upload File"}
          </label>
            <input
              class="hidden"
              type="file"
              id="file-upload"
              onchange={props.onFileChange}
          />
              
              <div class="truncate text-xs text-white px-1">
                {props.file ? <label title={props.file?.name}>{props.file?.name}</label> : <span>&nbsp;</span>}
              </div>
              {props.file && <button onclick={props.onUpload} class="button button-green block mx-auto mb-4">Send</button>}
              <input class="text-sm hidden"
                type="file" id="file-upload" onchange={props.onFileChange}
              />
              <button
                class="button button-blue mx-auto flex items-center"
                onclick={handleNoteClick}
              >
                Show Notes
              </button>
            </div>
          ) : (
            <div class="w-full">
              <Notes
                notes={props.notes}
                modalNote={props.modalNote}
                modalTarget={props.modalTarget}
                showmodal={props.showmodal}
                onOpenModal={props.onOpenModal}
                onCloseModal={props.onCloseModal}
                onNoteClick={handleNoteClick}
                onSelectNote={props.onSelectNote}
                onSelectTarget={props.onSelectTarget}
                onModalEdit={props.modalEdit}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Main
