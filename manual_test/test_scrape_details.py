import core.driver as cdriver
import parsers as prs

if __name__ == '__main__':
    store = input('Store:')
    url = input('URL:')

    # Initiate Driver Status
    driver = cdriver.Driver()

    pr = prs.select(store, 'details')

    oneline = pr.parse(driver)

    print(oneline)


