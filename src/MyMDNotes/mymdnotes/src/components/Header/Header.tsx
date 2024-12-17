import { Component } from "solid-js"


interface HeaderProps {
  token_name:string ;
}
const handleLogOut = (): void => {
  // Redirect to logout url
  const ask = confirm('Are you sure you want to logout?')
  if (ask)
    window.location.href = '.auth/logout'
}


const Header: Component<HeaderProps> = (props) => {
  return (
    <header class="relative z-50 flex justify-between items-center p-4 shadow-lg">
      <div class="flex items-center">
        <img class="max-w-[100px] w-full mr-4" src="/src/assets/images/icons/Logotype_gradient.svg" alt="zionai" />
        <h1 class="font-bold text-sm">My MD Notes</h1>
      </div>
      <div class='space-x-2'>
        {props.token_name && <>
          <span class='text-sm font-semibold mr-3'>{props.token_name}</span>
          <button class="button button-blue" onClick={handleLogOut}>Logout</button>
        </>}
        {!props.token_name && <>
          <button class="button button-green">Login</button>
        </>}
      </div>
    </header>
  )
}

export default Header