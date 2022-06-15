import dns.resolver

dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

class color:
    BOLD = '\033[1m'
    END = '\033[0m'

check = ""
while check != "single" and check != "multiple":
    check = input("Check a " + color.BOLD + "single" + color.END + " domain or " + color.BOLD + "multiple" + color.END + "? ").lower()

    if (check != "single") and (check != "multiple"):
        print ("Please enter \'single\' or \'multiple\'")

# get domain(s) to check
domains = []
i = 0
numDomains = 0
numSupportableDomains = 0
numUnsupportableDomains = 0
numUnknownDomains = 0

if check == "single":
    resp = input("Domain to check: ")
    domains.append(resp)
elif check == "multiple":
    path = input("Path to list of domains to check: ")
    resp = open(path, "r")
    for line in resp.read().splitlines():
        domains.append(line)

output = ""
while output != "console" and output != "csv":
    output = input("Output in "+ color.BOLD + "console" + color.END + " or as " + color.BOLD + "csv" + color.END + "? ").lower()

    if (output != "console") and (output != "csv"):
        print ("Please enter \'console\' or \'csv\'")

# remove duplicates
domains = list(dict.fromkeys(domains))

exchangeOnline = "mail.protection.outlook.com"
mx = ""
isExchangeOnline = False

outlookSpf = "spf.protection.outlook.com"
spf = ""
isOutlookSpf = False

if output == "console":
    print("")
    print(color.BOLD + "domain, isExchangeOnline, isOutlookSpf, isSupportable" + color.END)

for domain in domains:
    numDomains += 1

    try:
        # use mx record to see if domain uses exchange online
        mxAnswers = dns.resolver.query(domain, 'MX')
        mx = str(mxAnswers.response)
        isExchangeOnline = exchangeOnline in mx

        # use spf check to see if domain allows outlook to send emails on its behalf
        spfAnswers = dns.resolver.query(domain, 'TXT')
        spf = str(spfAnswers.response)
        isOutlookSpf = outlookSpf in spf
    except:
        numUnknownDomains += 1

    if isExchangeOnline and isOutlookSpf:
        # exchangeOnline = true + exchangeSpf = true *should be* supportable
        isSupportable = True
        numSupportableDomains += 1
    elif isExchangeOnline and (not isOutlookSpf):
        # exchangeOnline = true + exchangeSpf = false can mean a few different things (like hybrid deployments), but is generally not supportable
        isSupportable = False
        numUnsupportableDomains += 1
    elif (not isExchangeOnline) and isOutlookSpf:
        # unclear what this state represents → unclear if supportable (probably not?)
        isSupportable = "Unknown"
        numUnknownDomains += 1
    elif (not isExchangeOnline) and (not isOutlookSpf):
        # exchangeOnline = false + exchangeSpf = false is definitely not supportable
        isSupportable = False
        numUnsupportableDomains += 1

    if output == "console":
        print(domain + ", " + str(isExchangeOnline) + ", " + str(isOutlookSpf) + ", " + str(isSupportable))

print("Supported domains: " + str(numSupportableDomains) + " (" + str(round(numSupportableDomains/numDomains,2)*100) + "%)")
print("Unsupported domains: " + str(numUnsupportableDomains) + " (" + str(round(numUnsupportableDomains/numDomains,2)*100) + "%)")
print("Unknown domains: " + str(numUnknownDomains) + " (" + str(round(numUnknownDomains/numDomains,2)*100) + "%)")
print("")
