from django.shortcuts import render
from .models import *
from django.views.generic.list import ListView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError

# test comment


def GetOrdinal(number):
    """
    1 to 1st,
    2 to 2nd,
    etc.

    Pulled from: https://stackoverflow.com/a/54101248
    """
    if type(number) != type(1):
        try:
            number = int(number)
        except:
            raise ValueError("This number is not an Int!")
    lastdigit = int(str(number)[len(str(number)) - 1])
    last2 = int(str(number)[len(str(number)) - 2 :])
    if last2 > 10 and last2 < 13:
        return str(number) + "th"
    if lastdigit == 1:
        return str(number) + "st"
    if lastdigit == 2:
        return str(number) + "nd"
    if lastdigit == 3:
        return str(number) + "rd"
    return str(number) + "th"


class BoopInfiniteList(ListView):
    model = Boop
    paginate_by = 8
    context_object_name = "texts"
    template_name = "home.html"
    ordering = ["-num_foops", "creation_ts"]

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        if query:
            return qs.filter(boop_text__icontains=query)
        return qs


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def handle_bots(request):
    nowTime = timezone.now()
    clientIP = get_client_ip(request)
    lastPOSTSubmission = UserPOSTSubmission.objects.filter(user_ip=clientIP).first()
    if not lastPOSTSubmission:
        newPOSTSubmission = UserPOSTSubmission(user_ip=clientIP, last_submitted=nowTime)
        newPOSTSubmission.save()
    else:
        if abs(lastPOSTSubmission.last_submitted - nowTime).total_seconds() < 1.5:
            newFoopWarning = UserPOSTSubmissionWarning(
                user_ip=clientIP,
                last_submitted=lastPOSTSubmission.last_submitted,
                submit_attempt=nowTime,
            )
            newFoopWarning.save()
            lastPOSTSubmission.last_submitted = nowTime
            lastPOSTSubmission.save()
            return False
        else:
            lastPOSTSubmission.last_submitted = nowTime
            lastPOSTSubmission.save()
    return True


@csrf_exempt
def sendFoop(request):
    if request.method == "POST":
        if not handle_bots(request):
            return HttpResponse(
                json.dumps({"error_msg": "Error: you are sending foops too fast!"}),
                content_type="application/json",
                status=400,
            )
        boopInst = get_object_or_404(Boop, pk=request.POST.get("textId"))
        boopInst.num_foops = boopInst.num_foops + 1
        boopInst.save()
        return HttpResponse(
            json.dumps({"num_foops": boopInst.num_foops}),
            content_type="application/json",
            status=201,
        )

    return HttpResponse(status=500)


@csrf_exempt
def sendBoop(request):
    if request.method == "POST":
        boopText = request.POST.get("boopText")
        if boopText is not None:
            newBoop = Boop(boop_text=boopText)
            if not handle_bots(request):
                return HttpResponse(
                    json.dumps(
                        {"error_msg": "Error: you are submitting content too fast!"}
                    ),
                    content_type="application/json",
                    status=400,
                )
            try:
                newBoop.save()
                messages.success(request, "Nice! You just shooped a boop!")
                return HttpResponse(
                    json.dumps({"boop_id": newBoop.pk}),
                    content_type="application/json",
                    status=201,
                )
            except ValidationError as e:
                return HttpResponse(
                    json.dumps(
                        {
                            "error_msg": "Error: this boop has not met the community standards for toxicity. Please reword your boop."
                        }
                    ),
                    content_type="application/json",
                    status=400,
                )
            except IntegrityError as e:
                if "UNIQUE constraint" in e.args[0]:
                    return HttpResponse(
                        json.dumps(
                            {
                                "error_msg": "This boop has already been shooped. Please select a unique boop."
                            }
                        ),
                        content_type="application/json",
                        status=400,
                    )

    return HttpResponse(
        json.dumps(
            {
                "error_msg": "There was something wrong with your boop. Please try a different one."
            }
        ),
        content_type="application/json",
        status=400,
    )


def viewBoop(request, boop_id):
    print("here")
    boopInst = get_object_or_404(Boop, pk=boop_id)
    rank = Boop.objects.filter(num_foops__gt=boopInst.num_foops).count()
    totalNumBoops = Boop.objects.all().count()
    print("here1")
    rankFraction = rank / totalNumBoops
    if rankFraction < (1 / 3):
        rankColor = "bg-success"
    elif rankFraction < (2 / 3):
        rankColor = "bg-info"
    else:
        rankColor = "bg-secondary"
    homepageLink = request.build_absolute_uri(reverse("Ranker:texts_list"))
    viewBoopLink = request.build_absolute_uri(
        reverse("Ranker:view_boop", kwargs={"boop_id": boopInst.id})
    )
    return render(
        request,
        "boop_direct.html",
        {
            "boop": boopInst,
            "numBoops": totalNumBoops,
            "boopRank": GetOrdinal(rank + 1),
            "rankColor": rankColor,
            "homeLink": homepageLink,
            "viewBoopLink": viewBoopLink,
        },
    )


@csrf_exempt
def sendReport(request):
    if request.method == "POST":
        if not handle_bots(request):
            return HttpResponse(
                json.dumps(
                    {"error_msg": "Error: you are submitting content too fast!"}
                ),
                content_type="application/json",
                status=400,
            )
        reportText = request.POST.get("reportText")
        boopID = request.POST.get("boopId")
        if reportText is not None and boopID is not None:
            boopToReport = get_object_or_404(Boop, pk=boopID)
            newReport = BoopReport(boop=boopToReport, report_reason=reportText)
            newReport.save()
            messages.success(
                request,
                "Thank you for your report. Our staff will be looking into this boop shortly. If it is found to be offensive, it will be removed from the site.",
            )
            return HttpResponse(status=201)

    return HttpResponse(status=400)


def aboutPage(request):
    testObj = get_object_or_404(Boop, pk=1)
    return render(request, "about.html")
