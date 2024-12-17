import { Component, createSignal, For } from "solid-js";
import { AiOutlineEdit } from "solid-icons/ai";
import { FiSearch } from "solid-icons/fi";
import { IoExpand } from "solid-icons/io";
import Modal from "../Modal";
import { INote } from "../../../interfaces";

interface NotesProps {
  notes: INote[];
  modalNote: INote | null;
  modalTarget: string;
  showmodal: boolean;
  onNoteClick: () => void;
  onOpenModal: () => void;
  onCloseModal: () => void;
  onSelectNote: (note: INote) => void;
  onSelectTarget: (type: string) => void;
  onModalEdit: (note: INote) => void;
}

const Notes: Component<NotesProps> = (props) => {
  const [selectedNote, setSelectedNote] = createSignal<INote | null>(null);

  return (
    <>
      <section class="relative z-10 max-w-[1000px] w-full h-[calc(100vh-65px)] mx-auto flex">
        {/* Sidebar */}
        <aside class="w-1/3 bg-gray-200 p-4 overflow-y-scroll">
          <h2 class="mb-4 text-lg font-bold text-center">File List</h2>
          <button class="button button-green mb-4" onclick={props.onNoteClick}>Back</button>
          <div class="relative mb-4">
            <input
              type="search"
              class="w-full outline-none resize-none border rounded-lg text-black p-2 pr-10"
              placeholder="Search files..."
            />
            <FiSearch class="absolute right-3 top-1/2 -translate-y-1/2" />
          </div>
          <For each={props.notes}>
            {(note) => (
              <div
                class="flex flex-col p-4 mb-2 bg-white shadow-md rounded cursor-pointer hover:bg-gray-300"
                onclick={() => setSelectedNote(note)}
              >
                <div>
                  <label class="font-bold">File ID:</label> <span>{note.file_id}</span>
                </div>
                <div>
                  <label class="font-bold">Date:</label> <span>{new Date(note.updated).toLocaleString()}</span>
                </div>
              </div>
            )}
          </For>
        </aside>

        {/* Main Content Area */}
        <main class="w-2/3 p-6 bg-white shadow-lg overflow-y-scroll">
          {selectedNote() ? (
            <div class="flex flex-col bg-gray-100 p-4 rounded">
              {/* Transcript Section */}
              <div class="mb-4">
                <div class="flex items-center justify-between">
                  <label class="font-bold uppercase">Transcript</label>
                  <button
                    class="px-3 text-blue-500"
                    onclick={() => {
                      const note = selectedNote();
                      if (note) {
                        props.onSelectNote(note);
                        props.onSelectTarget("transcription");
                        props.onOpenModal();
                      }
                    }}
                  >
                    <IoExpand />
                  </button>
                </div>
                <textarea
                  rows={4}
                  class="w-full border outline-none resize-none p-2 mt-2"
                  value={selectedNote()?.transcription || ""}
                  readonly
                />
              </div>

              {/* Notes Section */}
              <div>
                <div class="flex items-center justify-between">
                  <label class="font-bold uppercase">Notes</label>
                  <button
                    class="px-3 text-blue-500"
                    onclick={() => {
                      const note = selectedNote();
                      if (note) {
                        props.onSelectNote(note);
                        props.onSelectTarget("edit");
                        props.onOpenModal();
                      }
                    }}
                  >
                    <AiOutlineEdit />
                  </button>
                </div>
                <textarea
                  rows={4}
                  class="w-full border outline-none resize-none p-2 mt-2"
                  value={selectedNote()?.updatedNotes || ""}
                  readonly
                />
              </div>
            </div>
          ) : (
            <div class="text-gray-500">Select a File ID from the sidebar to view details.</div>
          )}
        </main>

      </section>

      {/* Modal */}
      {props.showmodal && (
        <Modal
          note={props.modalNote}
          target={props.modalTarget}
          onCloseModal={props.onCloseModal}
          edit={props.onModalEdit}
        />
      )}
    </>
  );
};

export default Notes;