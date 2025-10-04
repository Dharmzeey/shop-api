from users.serializers import UserInfoSerializer
from users.models import User

def return_user_details(user, request):
  """
  Gets user details and returns
  _summary_

  Args:
      user (_type_): _description_
      request (_type_): _description_

  Returns:
      _type_: _description_
  """
  current_user = User.objects.get(email=user.email)
  user_info_serializer = UserInfoSerializer(instance=current_user.user_info, context = {'request': request}).data
  return user_info_serializer
