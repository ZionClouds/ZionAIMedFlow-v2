import { Component } from "solid-js"
import { INote } from "../../../interfaces"

interface ModalProps {
    note: INote | null
    target: string,
    onCloseModal: () => void,
    edit: (note: INote) => void
}

const Modal: Component<ModalProps> = (props) => {
    return (
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[999999]">
            <div class="bg-slate-50 text-black rounded shadow-lg w-[95%] md:w-3/4 h-3/4 flex flex-col overflow-clip">
                <div class='flex bg-[#3D5CAA] text-white'>
                    <div class="flex-grow"></div>
                    <div class='p-2'><button onClick={props.onCloseModal}>[X]</button></div>
                </div>
                {props.target === 'transcription' &&
                    <h2 class="text-xl font-bold px-2">Transcript</h2>
                }
                {props.target === 'edit' &&
                    <h2 class="text-xl font-bold px-2">Edit Medical Notes</h2>
                }

                {props.target === 'transcription' &&
                    <textarea
                        class="w-full h-full m-2 p-2 outline-none resize-none border text-black"
                        value={props.note?.transcription} readOnly
                    />
                }
                {props.target === 'edit' &&
                    <textarea class="w-full h-full m-2 p-2 outline-none resize-none border text-black"
                        onInput={(e) => props.note!.updatedNotes = (e.target as HTMLTextAreaElement).value}
                        value={props.note?.updatedNotes}
                    />
                }
                <div class="flex space-x-2 p-4">
                    {true &&
                        <button
                            class="button button-blue"
                            onClick={() => props.edit(props.note as INote)}
                        >
                            Save
                        </button>
                    }
                    <button class="button button-green" onClick={props.onCloseModal}>
                        Close
                    </button>
                </div>
            </div>
        </div>
    )
}

export default Modal
