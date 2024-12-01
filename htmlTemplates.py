css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #e0e0e0
}
.chat-message.bot {
    background-color: rgb(240, 242, 246);
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: black;
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://img.freepik.com/premium-psd/blue-robot-with-blue-head-that-says-robot-it_1217673-194073.jpg">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''
# https://tse3.mm.bing.net/th?id=OIP.enhhyI5hehixI-gMSimoEgHaHa&pid=Api

user_template = '''
<div class="chat-message user">
   <div class="avatar">
        <img src="https://img.freepik.com/premium-vector/girl-s-face-with-beautiful-smile-female-avatar-website-social-network_499739-527.jpg">
    </div>     
    <div class="message">{{MSG}}</div>
</div>
'''