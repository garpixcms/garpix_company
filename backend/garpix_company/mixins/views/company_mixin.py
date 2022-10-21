from rest_framework.permissions import IsAuthenticated


class GarpixCompanyViewSetMixin:

    permission_classes_by_action = {'create': [IsAuthenticated]}

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]
